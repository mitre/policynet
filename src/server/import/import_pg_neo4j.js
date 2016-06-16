var neo4j = require('neo4j'),
pg = require('pg'),
_ = require('lodash'),
promise = require('bluebird');
var config = {
	neo4j_url   : 'http://localhost:7474'
};


function pg2neo(pg_user, pg_pass, pg_host, pg_db){

	var pg_conn = "postgres://" + pg_user + ":" + pg_pass + "@" + pg_host + "/" + pg_db;

	console.log(pg_conn);
	var pg_client = new pg.Client(pg_conn);
	var neo4j_conn = new neo4j.GraphDatabase(config.neo4j_url);

	var initiation_cypher = [
	"MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r",
	"CREATE INDEX ON :Law(name)",
	"CREATE CONSTRAINT ON (n:Law) ASSERT n.url IS UNIQUE",
	]

	var tx_size = 10000;
	var tx = neo4j_conn.beginTransaction();

	var node_query = "MERGE (d:Law {name: {name}, heading: {heading}, text: {text}, url: {url}, type: {type}, l1: {l1}, l2: {l2}, l3: {l3}, l4: {l4}})";
	var edge_query = "MATCH (n:Law {url: {source_url}}), (m:Law {url: {target_url_broad}}) CREATE (n)-[:References {targetURLbroad: {target_url_broad}, context: {context}}]->(m)";

	return promise.all([pg_connect(pg_client)].concat(initiation_cypher.map(function(i){return neo4j_cypher(neo4j_conn, i);})))
	.then(function(result){
		return new promise(function(resolve, reject){


			pg_query(pg_client, "SELECT COUNT(*) AS count FROM nodes")
			.then(function(count){
				var count = count[0].count;
				console.log("started nodes");
				return promise.map(Array(Math.ceil(count / tx_size)), function(n, batch){
					console.log("node batch #", batch);
					var offset = batch * tx_size;
					return pg_query(pg_client, "SELECT node AS name, heading, url, doctype AS type, text, l1, l2, l3, l4 FROM nodes ORDER BY id ASC LIMIT " + tx_size + " OFFSET " + offset)
					.then(function(data){

						return promise.map(data, function(n,i){
							process.stdout.clearLine();
							process.stdout.cursorTo(0);
							process.stdout.write((batch * tx_size + i).toString());
							_.forEach(n, function(v,k){
								if (v === null){
									n[k] = "";
								}
							});
							return new promise(function(resolve, reject){
								tx.cypher({query: node_query, params: n}, function(err){
									if (err){
										console.log(4);
										console.log(err);
										console.log(err.message);
										reject(err);
									}
									resolve();
								});
							});
						}, {concurrency: 1})
						.then(function(){
							process.stdout.clearLine();
							console.log("progress: " + ((batch * tx_size + data.length) / count * 100).toFixed(2) + "%")
							return new promise(function(resolve, reject){
								tx.commit(function(err){
									if (err){
										console.log(6);
										console.log(err);
										console.log(err.message);
										reject(err);
									}
									console.log("nodes " + (batch * tx_size + data.length) + " done");
									tx = neo4j_conn.beginTransaction();
									resolve();
								});
							});
						});
					});
				}, {concurrency: 1})
			})
			.then(function(){
				return pg_query(pg_client, "SELECT COUNT(*) AS count FROM edges")
			})
			.then(function(count){
				var count = count[0].count;
				console.log("started edges");
				return promise.map(Array(Math.ceil(count / tx_size)), function(e, batch){
					console.log("edge batch #", batch);
					var offset = batch * tx_size;
					return pg_query(pg_client, "SELECT source_url, target_url_broad, context FROM edges ORDER BY id ASC LIMIT " + tx_size + " OFFSET " + offset)
					.then(function(data){
						return promise.map(data, function(e,i){
							process.stdout.clearLine();
							process.stdout.cursorTo(0);
							process.stdout.write((batch * tx_size + i).toString());
							_.forEach(e, function(v,k){
								if (v === null){
									e[k] = "";
								}
							});
							return new promise(function(resolve, reject){
								tx.cypher({query: edge_query, params: e}, function(err){
									if (err){
										console.log(4);
										console.log(err);
										console.log(err.message);
										reject(err);
									}
									resolve();
								});
							});
						}, {concurrency: 1})
						.then(function(){
							process.stdout.clearLine();
							console.log("progress: " + ((batch * tx_size + data.length) / count * 100).toFixed(2) + "%")
							return new promise(function(resolve, reject){
								tx.commit(function(err){
									if (err){
										console.log(6);
										console.log(err);
										console.log(err.message);
										reject(err);
									}
									console.log("edges " + (batch * tx_size + data.length) + " done");
									tx = neo4j_conn.beginTransaction();
									resolve();
								});
							});
						});
					});
				}, {concurrency: 1})
			})

			.then(function(){
				return new promise(function(resolve, reject){
					tx.commit(function(err){
						if (err){
							console.log(6);
							console.log(err);
							console.log(err.message);
							reject(err);
						}
						console.log("last bit done");
						resolve();
					});
				});
			})
			.then(function(){
				pg_client.end();
				resolve();
			});
		});
	});
}

function pg_query(conn, query){
	return new promise(function(resolve, reject){
		conn.query(query,function(err, result){
			if (err){
				console.error("error running query", err);
				console.error("error running query", err.message);
				reject(err);
			}
			resolve(result.rows);
		})
	})
}

function pg_connect(conn){
	return new promise(function(resolve, reject){
		conn.connect(function(err){
			if (err){
				console.error("could not connecto postgres", err);
				console.error("could not connecto postgres", err.message);
				reject(err);
			}
			resolve();
		});
	});
}

function neo4j_cypher(conn, query){
	return new promise(function(resolve, reject){
		try{
			console.log(query)
			conn.cypher({query: query}, function(result, err){
				if (err && err.length){
					console.error('cypher error: ', err);
					console.error('cypher error: ', err.message);
					reject(err);
				}
				resolve(result);
			});
		}
		catch(err){
			if (err){
				console.error('cypher error 2: ', err);
				console.error('cypher error 2: ', err.message);
				reject(err);
			}
		}
	});
}
module.exports = {
	pg2neo: pg2neo
}
