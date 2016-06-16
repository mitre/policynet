var neo4j 			= require("neo4j"),
	elasticsearch	= require('elasticsearch'),
	promise			= require('promise'),
	_				= require('lodash'),
	rp 				= require('request-promise'),
	utils			= require('./utils.js'),
	config 			= require('./config.js'),
	chalk			= require('chalk');

var es_base_query = {
	index: 'nodelist',
	type: 'nodelist',
	size: 1000,
	fields: '',
	body: {
		query: {}
	}
};


var query_elastic = function(query, verbose){
	var elast_conn = new elasticsearch.Client({host: config.elastic_host});
	var start = new Date().getTime();
	verbose && utils.info(query);
	return new promise(function(resolve,reject){
		elast_conn.search(query, function(err, res){
			elast_conn.close();
			if (err){
				utils.error(err);
				reject(err);
			} else {
				var end = new Date().getTime();
				verbose && utils.info('Query ElasticSearch time: ' + (end - start)/1000);
				resolve(res);
			}
		})
	});
}

var query_elastic_suggest = function(query, verbose){
	var elast_conn = new elasticsearch.Client({host: config.elastic_host});
	var start = new Date().getTime();
	verbose && utils.info(query);
	return new promise(function(resolve,reject){
		elast_conn.suggest(query, function(err, res){
			elast_conn.close();
			if (err){
				utils.error(err);
				reject(err);
			} else {
				var end = new Date().getTime();
				verbose && utils.info('Query ElasticSearch time: ' + (end - start)/1000);
				resolve(res);
			}
		})
	});
}

var query_neo4j = function(query, params, verbose){
	var neo4j_conn = new neo4j.GraphDatabase(config.neo4j_url);
	var start = new Date().getTime();
	verbose && utils.info(query);
	verbose && utils.info(params);
	return new promise(function (resolve, reject){
		try {
			neo4j_conn.cypher({query: query, params: params}, function(err, query_results){
				if (err){
					reject(err);
				} else {
					if (query_results.length === 0){
						reject(new Error("emptyResult"));
					} else {
						var end = new Date().getTime();
						verbose && utils.info('Query Neo4J time: ' + (end - start)/1000);
						resolve(query_results);
					}
				}
			})
		} catch (err){
			utils.error(err.message);
		}
	})
}

var query_http = function(request, verbose){
	if (request.method === 'post'){
		//TODO
	} else if (request.method === 'get'){

		var options = {
			uri: request.url,
			json: true,
			method: 'get',
			headers: request.header,
			qs: request.query
		};
		options = _.merge(options, request.options)
	}
	verbose && utils.info(options);
	return rp(options);
}
module.exports = {
	query_neo4j: query_neo4j,
	query_elastic: query_elastic,
	es_base_query: es_base_query,
	query_elastic_suggest: query_elastic_suggest,
	query_http: query_http
};
