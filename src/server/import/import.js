var spawn 				= require('child_process').spawn,
	_					= require('lodash'),
	promise				= require('bluebird'),
	utils				= require('../js/utils.js')
	download_unzip 		= require('./download_unzip.js'),
	import_pg_neo4j		= require('./import_pg_neo4j.js'),
	import_neo4j_es		= require('./import_neo4j_es.js');

var pg_username = process.argv[2];
var pg_password = process.argv[3];
var pg_database = process.argv[4];

promise.resolve()
.then(function(){
	// download and zip USC and CFR
	return download_unzip.download_unzip();
})
.then(function(){
	// parse USC and CFR, save intermediary nodelist and edgelist in PostgreSQL
	return childSpawn("sh", [__dirname + "/parse.sh", pg_username, pg_password, pg_database]);
})
.then(function(){
	// ingest nodelist and edgeslit from PostgreSQL to Neo4J
	return import_pg_neo4j.pg2neo(pg_username, pg_password, 'localhost', pg_database);
})
.then(function(){
	// index nodelist to Elastic
	return import_neo4j_es.neo2es();
})

var childSpawn = function(exe, args){
	return new promise(function(resolve, reject){
		utils.warning([exe].concat(args).join(" "));
		try {
			var parse = spawn(exe, args, {encoding: 'utf8', cwd: __dirname, stdio: [0,1,2]});
			parse.on('close', function(code){
				console.log('Done');
				resolve();
			});
		} catch (e){
			console.error("encountering error!");
			console.error(e.message);
			reject(e);
		}
	});
}
