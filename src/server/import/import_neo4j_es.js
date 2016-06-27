var neo4j = require('neo4j'),
	elasticsearch = require('elasticsearch'),
	promise = require('bluebird'),
	fs = require("fs");

var config = {
	neo4j_url	: 'http://localhost:7474',
	elastic_host: 'localhost:9200'
};


var client = new elasticsearch.Client({
	host: config.elastic_host,
	requestTimeout: 360000000 // some ridiculously large number to prevent timeout
});
var db = new neo4j.GraphDatabase(config.neo4j_url);

var batch_es = 1000, // number of documents per batch to be imported in bulk
	batch_neo4j = 10000,
	promises = [];

function neo2es(){
	return client.indices.delete({
			index: "_all"
		}).then(function(){
			return client.indices.create({
				index: "nodelist",
				type: "nodelist",
				body: {
					"mappings": {
						"nodelist": {
							"properties" : {
								"label" : {"type" : "string","index": "not_analyzed"},
								"heading" : {"type" : "string", "index": "not_analyzed"},
								"id" : {"type" : "integer","index": "not_analyzed"},
								"l1" : {"type" : "string","index": "not_analyzed"},
								"l2" : {"type" : "string","index": "not_analyzed"},
								"l3" : {"type" : "string","index": "not_analyzed"},
								"l4" : {"type" : "string","index": "not_analyzed"},
								"name" : {"type" : "string","index": "not_analyzed"},
								"name_suggest" : {"type" : "completion", "analyzer": "whitespace_analyzer", "search_analyzer": "whitespace_analyzer", "payloads": true},
								"text" : {"type" : "string", "analyzer": "stemmer_analyzer"},
								"type" : {"type" : "string","index": "not_analyzed"},
								"url" : {"type" : "string","index": "not_analyzed"}
							}
						}
					},
					"settings": {
						"analysis": {
							"analyzer": {
								"stemmer_analyzer": {
									"tokenizer": "standard",
									"filter": [
										"standard",
										"lowercase",
										"stemmer_filter"
									]
								},
								"edgeNGram_analyzer":{ //not used right now
									"type": "custom",
									"tokenizer": "whitespace",
									"filter": [
										"standard",
										"lowercase",
										"edgeNGram_filter"
									]
								},
								"whitespace_analyzer":{
									"type": "custom",
									"tokenizer": "whitespace",
									"filter":[
										"standard",
										"lowercase"
									]
								}
							},
							"filter": {
								"stemmer_filter": {
									"type": "stemmer",
									"name": "english"
								},
								"edgeNGram_filter": { //not used right now
									"type": "edgeNGram",
									"min_gram": 2,
									"max_gram": 20,
									"token_chars": ["letter", "digit"]
								}
							},
							"tokenizer": { //not used right now
								"edgeNGram_tokenizer": {
									"type": "edgeNGram",
									"min_gram": 2,
									"max_gram": 20,
									// "token_chars": ["letter", "digit"]
								}
							}
						}
					}
				}
			});
		}).then(function(){
			console.log("created index")
			return new promise(function(resolve, reject){
				db.cypher({
					query: "MATCH (n) RETURN COUNT(n) AS count",
					params: {}
				}, function(err, results){
					var count = results[0].count
					console.log("got nodes:", count);
					var promises = [];

					promise.map(Array(Math.ceil(count / batch_neo4j)), function(n, batch){
						var start = batch * batch_neo4j;
						return getNodesFromNeo4j(start, batch_neo4j)
						.then(insertToES);
					}, {concurrency: 2})
					.then(function(){
						console.log("import into elasticsearch completed")
						client.close();
						resolve();
					});
				});
			});
		});
}

function getNodesFromNeo4j(start, batch){
	return new promise(function(resolve, reject){
		try{
			db.cypher({
				query: "MATCH (n) return labels(n) AS label, id(n) AS id, n.type AS type, n.url AS url, n.name AS name, n.l1 AS l1, n.l2 AS l2, n.l3 AS l3, n.l4 AS l4, n.heading AS heading, n.text AS text skip " + start + " limit " + batch,
				params: {}
			}, function(err, results){
				if (err){
					console.error("err")
					console.error(err);
					reject(err);
				}
				console.log("got", results.length, " nodes from Neo4J from:", start + ", with id from", results[0].id, "to", results[results.length - 1].id);
				resolve(results);
			});
		} catch (err){
			console.error("err");
			console.error(err.message);
			console.error(err.stack);
			reject(err);
		}
	});
}

function insertToES(results){
	var promises = [], bulk_request = [];
	return promise.map(Array(Math.ceil(results.length / batch_es)), function(n, batch){
		var start = batch * batch_es;
		var end = Math.min(results.length, (batch + 1) * batch_es);
		results.slice(start, end).forEach(function(n){
			bulk_request.push({index:{
				_index: 'nodelist',
				_type: 'nodelist',
				_id: n.id
			}});
			n.label = n.label[0];
			n.name_suggest = {
				"input": n.name,
				"payload": {"id": n.id}
			};
			bulk_request.push(n);
		});
		promises.push(client.bulk({
			body: bulk_request
		}));
		return promise.all(promises).then(function(){
		});
	}, {concurrency: 1})
}
module.exports = {
	neo2es: neo2es
};
