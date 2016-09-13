var net				= require('net'),
	spawn			= require('child_process').spawn,
	chalk			= require("chalk"),
	promise			= require('promise'),
	_				= require('lodash'),
	chroma			= require('chroma-js'),
	pd 				= require('pretty-data').pd,
	query_utils		= require('./query.utils.js'),
	config			= require('./config.js'),
	packing			= require('./graph.packing.js'),
	parse 			= require('./parse.js');

var logic = {};

logic.sections = function(req, res){
	var query = "match (n) where n.l1 = {l1} return distinct n.l2 limit 100"
	var params = {"l1" : req.query.query};
	query_utils.query_neo4j(query, params).then(function(result){
		res.json(result.map(function(e){
			return parseInt(e["n.l2"])
		}).sort(function(a,b){return a - b;}));
	})
}

logic.network_neighborhood = function(req,res){
	var params = req.query;
	params.node = parseInt(params.node);
	var query = "MATCH (a) WHERE id(a) = {node} "
			  + "MATCH (a)-[r1*1.." + params.hop + "]-(m) "
			  + "WITH COLLECT(DISTINCT(id(m))) + id(a) AS coll "
			  + "MATCH (m)-[r]-(n) "
			  + "WHERE id(n) IN coll AND id(m) IN coll "
			  + "RETURN DISTINCT r.context AS r_context, r.type AS r_type, r.targetURLbroad AS r_target, id(n) AS n_id, n.l1 AS n_l1, n.l2 AS n_l2, n.l3 AS n_l3, n.heading AS n_name, n.url AS n_url, id(m) AS m_id, m.l1 AS m_l1, m.l2 AS m_l2, m.l3 AS m_l3, m.heading AS m_name, m.url AS m_url";
	query_layout_packing(query, params, [params.node], false).then(function(result){
		res.json(result);
	}, function(err){
		res.status(500).json(err.message);
	})
}

logic.network_local = function(req, res){
	var params = req.query;
	params.node = parseInt(params.node);
	var query = "MATCH (n) WHERE id(n) = {node} "
			  + "MATCH (n)-[r]-(m:Law) "
			  + "WITH m AS refs "
			  + "OPTIONAL MATCH m-[r2]-refs "
			  + "RETURN DISTINCT r.context AS r_context, r.type AS r_type, r.targetURLbroad AS r_target, id(n) AS n_id, n.l1 AS n_l1, n.l2 AS n_l2, n.l3 AS n_l3, n.heading AS n_name, n.url AS n_url, id(m) AS m_id, m.l1 AS m_l1, m.l2 AS m_l2, m.l3 AS m_l3, m.heading AS m_name, m.url AS m_url";

	query_layout_packing(query, params, [params.node], false).then(function(result){
		res.json(result);
	}, function(err){
		res.status(500).json(err.message);
	})
}

logic.network_neo4j = function(req, res){
	var params = req.query;

	params.query = params.query === " " ? "" : params.query;
	var query = "MATCH (n:Law {"
			  + (params.l1 !== 'All' ? "l1: {l1}" : "")
			  + (params.l1 !== 'All' && params.l2 !== 'All' ? ",l2: {l2}" : "")
			  + "}) "
			  + (params.query !== "" ? "where n.text =~ {query} " : "")
			  + "OPTIONAL MATCH n-[r:References]-(m:Law) "
			  + "RETURN DISTINCT r.context AS r_context, r.type AS r_type, r.targetURLbroad AS r_target, id(n) AS n_id, n.l1 AS n_l1, n.l2 AS n_l2, n.l3 AS n_l3, n.heading AS n_name, n.url AS n_url, id(m) AS m_id, m.l1 AS m_l1, m.l2 AS m_l2, m.l3 AS m_l3, m.heading AS m_name, m.url AS m_url "
			  + "LIMIT {limit}";
	params.limit = parseInt(params.limit);
	params.query = '.*(?i)' + params.query + '.*';

	query_layout_packing(query, params, []).then(function(result){
		res.json(result);
	}, function(err){
		res.status(500).json(err.message);
	})
}

logic.network_es = function(req, res, singletons){
	var params = req.query;
	params.query = (params.query === undefined || params.query === " ") ? "" : params.query.toLowerCase();

	var es_query = _.cloneDeep(query_utils.es_base_query);
	es_query.size = params.limit;
	es_query_question = es_query.body.query = {"bool": {"must": [], "minimum_should_match": 0}};
	es_query_question.bool.must.push({term: { label: "Law" }});
	if (params.l1 !== 'All') {
		es_query_question.bool.must.push({term: { l1: params.l1 }});
	}
	if (params.l1 !== 'All' && params.l2 !== 'All') {
		es_query_question.bool.must.push({term: { l2: params.l2 }});
	}
	if (params.query !== '') {

		var queryObj = parseQuery(params.query);
		es_query_question.bool.should = [];
		es_query_question.bool.must_not = [];

		queryObj.exactMust.forEach(function(phrase){
			es_query_question.bool.must.push({"match_phrase": {"text": phrase}});
		})
		queryObj.fuzzyMust.forEach(function(phrase){
			var fuzzy = fuzziness(phrase);
			es_query_question.bool.must.push({"fuzzy": {"text": fuzzy}});
		})
		queryObj.exactShould.forEach(function(phrase){
			es_query_question.bool.should.push({"match_phrase": {"text": phrase}});
		})
		queryObj.fuzzyShould.forEach(function(phrase){
			var fuzzy = fuzziness(phrase);
			es_query_question.bool.should.push({"fuzzy": {"text": fuzzy}});
		})
		queryObj.exactMustnot.forEach(function(phrase){
			es_query_question.bool.must_not.push({"match_phrase": {"text": phrase}});
		})
		queryObj.fuzzyMustnot.forEach(function(phrase){
			var fuzzy = fuzziness(phrase);
			es_query_question.bool.must_not.push({"fuzzy": {"text": fuzzy}});
		})

	}
	query_utils.query_elastic(es_query, true).then(function(results){
		params.nodeIdList = _.map(results.hits.hits, function(n){return parseInt(n._id)});
		var neo4j_query = "MATCH (n) WHERE id(n) IN {nodeIdList} "
						+ "optional match (n)-[r:References]-(m:Law) "
						+ "return distinct r.context AS r_context, r.type AS r_type, r.targetURLbroad AS r_target, id(n) AS n_id, n.l1 AS n_l1, n.l2 AS n_l2, n.l3 AS n_l3, n.heading AS n_name, n.url AS n_url, id(m) AS m_id, m.l1 AS m_l1, m.l2 AS m_l2, m.l3 AS m_l3, m.heading AS m_name, m.url AS m_url "
						+ "limit {limit}";

		params.limit = parseInt(params.limit);

		query_layout_packing(neo4j_query, params, params.nodeIdList, singletons).then(function(result){
			res.json(result);
		}, function(err){
			res.status(500).json(err.message);
		})
	}, function(err){
		res.status(500).json(err);
	})
}

var query_layout_packing = function(query, params, matchList, singletons){
	var parsed_json;
	var start, end;
	return query_utils.query_neo4j(query,params,true)
		.then(function(query_results){
			parsed_json = utils.neo4jtojson(query_results, matchList);
			start = new Date().getTime();
			return utils.java_layout({
				edges: parsed_json.edges,
				config: {
					layout_cc: "true",
					layout: "yifanhu"
				}
			});
		})
		.then(function(java_output){
			return new promise(function(resolve, reject){
				try {
					end = new Date().getTime();
					utils.info('Java layout time: ' + (end - start)/1000);

					var combined_output = utils.combine_output(java_output, parsed_json);
					if (singletons){
						combined_output.singletons.forEach(function(s){
							s.x = 0;
							s.y = 0;
							combined_output.clusters.push([s.id]);
							combined_output.nodes.push(s);
						});
						combined_output.singletons = [];
					}
					utils.info("done with layout");

					var packed_output = packing.clusterPacking(combined_output);
					utils.success("done with packing, sending results back to UI");
					resolve(packed_output);
				} catch(err){
					reject(err);
				}
			})
		}, function(err){
			utils.error("err.stack")
			utils.error(err.stack)
			if (err.message === "emptyResult"){
				utils.error("handling error: " + err.message + "...");
				return {status: "failed",
						message: "Query Result Empty."};
			} else {
				utils.error("throwing unknown error: " + err.message + "!");
				utils.error(err);
				return {status: "failed",
						message: err.message};
			}
		})
}

logic.node = function(req, res){
	var query = "MATCH (n) WHERE id(n) = {nodeid} RETURN n";
	var params = req.query;
	params.nodeid = parseInt(params.nodeid);

	query_utils.query_neo4j(query, params).then(function(result){
		res.json(result);
	}, function(err){
		res.status(500).json(err.message);
	});
}
logic.suggest = function(req, res){
	var es_query = {
		index: 'nodelist',
		body: {
			suggester: {
				text: req.query.prefix,
				completion: {
					field: req.query.field + "_suggest",
					size: parseInt(req.query.limit),
				}
			}
		}
	};

	query_utils.query_elastic_suggest(es_query).then(function(results){
		res.json(results);
	}, function(err){
		res.status(500).json(err);
	});
}

logic.parseQueryWrapper = function(req, res){
	res.json(parseQuery(req.query.query));
}

var parseQuery = function(query){
	query = _.trim(query);
	var quote_pos = getIndices(query, '"');
	if (quote_pos.length % 2 === 1){
		quote_pos.pop();
	}
	var result = {
		exactMust: [],
		fuzzyMust: [],
		exactShould: [],
		fuzzyShould: [],
		exactMustnot: [],
		fuzzyMustnot: []
	};
	var words = [];
	var modifiers, cat;
	// from first character to first quote
	words = words.concat(_.words(query.substring(0, quote_pos[0]), /[^, '"']+/g));
	for (var i = 0; i < Math.floor(quote_pos.length / 2); i++){
		// get modifier before quote: 1. get position of last space, 2.
		modifiers = query.substring(Math.max(0, query.substring(0, quote_pos[i * 2]).lastIndexOf(" ") + 1), quote_pos[i * 2]);
		// place phrase based on modifier
		cat = getCat(modifiers);

		result[cat].push(query.substring(quote_pos[i * 2] + 1, quote_pos[i * 2 + 1]));
		// collect loose terms
		words = words.concat(_.words(query.substring(quote_pos[i * 2 + 1] + 1, quote_pos[(i + 1) * 2] ? quote_pos[(i + 1) * 2] : query.length), /[^, '"']+/g));

	}

	// check for modifiers in front of loose words
	words.forEach(function(term){
		// get modifier

		word = term.replace(/[^a-zA-Z0-9]/g, '');
		if (word !== ""){
			modifiers = term.substring(0, term.indexOf(word[0]));
			cat = getCat(modifiers);
			result[cat].push(word);
		}

	})

	function getIndices(arr, val) {
		var indexes = [], i = -1;
		while ((i = arr.indexOf(val, i+1)) != -1){
			indexes.push(i);
		}
		return indexes;
	}

	function getCat(modifiers){
		if (_.includes(modifiers, "#")){
			cat = "fuzzy";
		} else {
			cat = "exact";
		}

		if (_.includes(modifiers, "-")){
			cat += "Mustnot";
		} else if (_.includes(modifiers, "?")){
			cat += "Should";
		} else {
			cat += "Must";
		}
		return cat;
	}
	return result;
}

var fuzziness = function(phrase){
	// var fuzziness;

	// if (phrase.length <= 3){
	// 	fuzziness = 0;
	// } else if (phrase.length <= 5){
	// 	fuzziness = 1;
	// } else {
	// 	fuzziness = 2;
	// }

	return {
		"value" :         phrase,
		"boost" :         1.0,
		"fuzziness" :     "AUTO",
		"prefix_length" : 3,
		"max_expansions": 50
	}
}

logic.visit = function(req, res){
	res.json();
}

logic.table_stats = function(req, res){
	var params = req.query;
	params.query = (params.query === undefined || params.query === " ") ? "" : params.query.toLowerCase();
	var matched_nodes_limit = 50;
	var es_query = _.cloneDeep(query_utils.es_base_query);
	es_query.size = 10000;
	es_query_question = es_query.body.query = {"bool": {"must": [], "minimum_should_match": 0}};
	es_query_question.bool.must.push({term: { label: "Law" }});
	if (params.l1 !== 'All') {
		es_query_question.bool.must.push({term: { l1: params.l1 }});
	}
	if (params.l1 !== 'All' && params.l2 !== 'All') {
		es_query_question.bool.must.push({term: { l2: params.l2 }});
	}
	if (params.query !== '') {

		var queryObj = parseQuery(params.query);
		es_query_question.bool.should = [];
		es_query_question.bool.must_not = [];

		queryObj.exactMust.forEach(function(phrase){
			es_query_question.bool.must.push({"match_phrase": {"text": phrase}});
		})
		queryObj.fuzzyMust.forEach(function(phrase){
			var fuzzy = fuzziness(phrase);
			es_query_question.bool.must.push({"fuzzy": {"text": fuzzy}});
		})
		queryObj.exactShould.forEach(function(phrase){
			es_query_question.bool.should.push({"match_phrase": {"text": phrase}});
		})
		queryObj.fuzzyShould.forEach(function(phrase){
			var fuzzy = fuzziness(phrase);
			es_query_question.bool.should.push({"fuzzy": {"text": fuzzy}});
		})
		queryObj.exactMustnot.forEach(function(phrase){
			es_query_question.bool.must_not.push({"match_phrase": {"text": phrase}});
		})
		queryObj.fuzzyMustnot.forEach(function(phrase){
			var fuzzy = fuzziness(phrase);
			es_query_question.bool.must_not.push({"fuzzy": {"text": fuzzy}});
		})

	}
	es_query.fields = ['id', 'l1', 'l2', 'l3', 'name'];
	query_utils.query_elastic(es_query).then(function(results){
		try {
			params.nodeIdList = _.map(results.hits.hits, function(n){return parseInt(n._id)});
			if (params.nodeIdList.length <= matched_nodes_limit){
				var neo4j_query = "MATCH (n) WHERE id(n) IN {nodeIdList} "
								+ "MATCH (n)-[r:References]-(m:Law) WHERE NOT (id(m) IN {nodeIdList}) "
								+ "RETURN COUNT(DISTINCT(m)) AS linked_count, COUNT(DISTINCT(r)) AS edge_count"

				query_utils.query_neo4j(neo4j_query,params)
					.then(function(query_results){
						var out = {
							nodes: _.map(results.hits.hits, function(n){return _.mapValues(n.fields, function(m){return m[0]})}),
							statistics: {
								"Linked Nodes": query_results[0].linked_count,
								"Edges": query_results[0].edge_count
							}
						}
						res.json(out);
					}, function(err){
						res.status(500).json(err.message);
					})
			} else {
				res.json({
					nodes: _.map(results.hits.hits, function(n){return _.mapValues(n.fields, function(m){return m[0]})}),
					statistics: {}
				})
			}

		} catch (err){
			utils.error(err.message);
		}

	}, function(err){
		res.status(500).json(err);
	})
}

logic.bill_search = function(req, res){
	var query = {
		url: config.sunlightapi.url + config.sunlightapi.bill_search,
		method: 'get',
		query: {
			query: req.query.query.replace(/[^\w\s]/gi, ' '),
			fields: "bill_type,bill_id,last_version.urls,number,congress,short_title,official_title",
			per_page: req.query.limit,
			page: req.query.page,
			order: req.query.order
		},
		header: {
			"X-APIKEY": config.sunlightapi.api_key
		},
		options: config.http_options
	}
	query_utils.query_http(query).then(function(result){

		res.json(result);
	})
}

logic.bill_get = function(req, res){
	var query = {
		url: config.sunlightapi.url + config.sunlightapi.bill_get,
		method: 'get',
		query: {
			bill_id: req.query.bill_id,
			fields: "last_version.urls"
		},
		header: {
			"X-APIKEY": config.sunlightapi.api_key
		},
		options: config.http_options
	}
	query_utils.query_http(query).then(function(result){
		if (result.count === 1){
			var type, url;
			if (req.query.action === "redline"){
				type = "xml";

			} else {
				type = req.query.action;
			}
			url = result.results[0].last_version.urls[type];
			query = {
				url: url,
				method: 'get',
				options: config.http_options
			};
			query_utils.query_http(query).then(function(text){
				if (req.query.action === "redline"){
					parse.redline(text).then(function(result){
						res.json(result);
					})
				} else if (type === 'xml'){
					res.send(pd.xml(text));
				// } else if (type === 'pdf'){

				} else {
					res.send("XML not available.");
				}
			})

		} else {
			//TODO: handle error
			res.status(404);
		}
	})
}

logic.get_text = function(req, res){
	var params = req.query;
	var query = "MATCH (n:Law {url: {url}}) return n.xml as xml";
	query_utils.query_neo4j(query,params,true).then(function(query_results){
		try{
			var xml_str = utils.xml_str(utils.process_xml(query_results[0].xml));
			if (params.format === "xml"){
				res.json(xml_str);
			} else if (params.format === "text"){
				res.json(utils.xml_text(xml_str));
			}
		} catch (err){
			utils.error('err');
			utils.error(err.stack);
			res.status(500).json(err.message);
		}
	}, function(err){
		res.status(500).json(err.message);
	})
}

var request = function(fun){
	var args = _.values(arguments);
	return function(req, res){

		if (!!fun){
			logic[fun].apply(null, [req, res].concat(_.values(args).slice(1)));
		}
	}
}

module.exports = {
	request: request
};
