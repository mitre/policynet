var neo4j = require('neo4j-driver'),
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
	var driver = neo4j.v1.driver('bolt://localhost');
	var neo4j_conn = driver.session();

	var initiation_cypher = [
	"MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r",
	"CREATE INDEX ON :Law(name)",
	"CREATE CONSTRAINT ON (n:Law) ASSERT n.url IS UNIQUE",
	]

	var tx_size = 10000;
	var tx;

	var node_query = "MERGE (d:Law {name: {name}, heading: {heading}, text: {text}, url: {url}, type: {type}, l1: {l1}, l2: {l2}, l3: {l3}, l4: {l4}})";
	var edge_query = "MATCH (n:Law {url: {source_url}}), (m:Law {url: {target_url_broad}}) CREATE (n)-[:References {targetURLbroad: {target_url_broad}, context: {context}}]->(m)";

	return promise.all([pg_connect(pg_client)].concat(initiation_cypher.map(function(i){return neo4j_conn.run(i);})))
	.then(function(result){
		tx = neo4j_conn.beginTransaction();
		return new promise(function(resolve, reject){
			pg_query(pg_client, "SELECT COUNT(*) AS count FROM nodes")
			.then(function(count){
				var count = count[0].count;
				var done = 0;
				console.log("started nodes");
				return promise.map(Array(Math.ceil(count / tx_size)), function(n, batch){
					console.log("node batch #", batch);
					var offset = batch * tx_size;
					console.time('select');
					return pg_query(pg_client, "SELECT node AS name, heading, url, doctype AS type, text, l1, l2, l3, l4 FROM nodes ORDER BY id ASC LIMIT " + tx_size + " OFFSET " + offset)
					.then(function(data){
						console.timeEnd('select');
						console.time("node batch # " + batch);
						return promise.map(data, function(n,i){
							process.stdout.clearLine();
							process.stdout.cursorTo(0);
							process.stdout.write(done.toString());
							_.forEach(n, function(v,k){
								if (v === null){
									n[k] = "";
								}
							});
							done ++;
							return tx.run(node_query, n);
						}, {concurrency: 1})
						.then(function(){
							process.stdout.clearLine();
							process.stdout.cursorTo(0);
							console.timeEnd("node batch # " + batch);
							console.time("commit node batch # " + batch);
							console.log("progress: " + (done / count * 100).toFixed(2) + "%")
							return tx.commit().then(function(){
								console.log("nodes " + done + " done");
								console.timeEnd("commit node batch # " + batch);
								tx = neo4j_conn.beginTransaction();
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
				var done = 0;
				console.log("started edges");
				return promise.map(Array(Math.ceil(count / tx_size)), function(e, batch){
					console.log("edge batch #", batch);
					var offset = batch * tx_size;
					console.time('select');
					return pg_query(pg_client, "SELECT source_url, target_url_broad, context FROM edges ORDER BY id ASC LIMIT " + tx_size + " OFFSET " + offset)
					.then(function(data){
						console.timeEnd('select');
						console.time("edge batch # " + batch);
						return promise.map(data, function(e,i){
							process.stdout.clearLine();
							process.stdout.cursorTo(0);
							process.stdout.write(done.toString());
							_.forEach(e, function(v,k){
								if (v === null){
									e[k] = "";
								}
							});
							done ++;
							return tx.run(edge_query, e);
						}, {concurrency: 1})
						.then(function(){
							process.stdout.clearLine();
							process.stdout.cursorTo(0);
							console.timeEnd("edge batch # " + batch);
							console.time("commit edge batch # " + batch);
							console.log("progress: " + (done / count * 100).toFixed(2) + "%")
							return tx.commit().then(function(){
								console.log("edges " + done + " done");
								console.timeEnd("commit edge batch # " + batch);
								tx = neo4j_conn.beginTransaction();
							});
						});
					});
				}, {concurrency: 1})
			})

			.then(function(){
				return tx.commit();
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
