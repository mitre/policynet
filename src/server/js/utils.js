var pd 				= require('pretty-data').pd,
	xmldom			= require('xmldom'),
	_ 				= require("lodash"),
	chalk			= require("chalk"),
	fs 				= require("fs"),
	promise			= require("promise"),
	spawn			= require('child_process').spawn,
	net 			= require('net'),
	config 			= require('./config.js');

var java_layout = function(input_json){
	return childSpawn(config.java_home + "bin/java",
		['-classpath', '../java/policynet-layout.jar', 'org.mitre.policynet.policynet_layout.Layout'],
		function(client){
			client.write(JSON.stringify(input_json));
			client.end();
		});
}

var combine_output = function(java_output, parsed_json){
	var combined_output = parsed_json;
	java_output = JSON.parse(java_output);
	combined_output.clusters = java_output.connectedComponents;
	combined_output.nodes.forEach(function(n){
		n.x = java_output.positions[n.id][0];
		n.y = java_output.positions[n.id][1];
	})
	combined_output.java = java_output;
	return combined_output;
}

var neo4jtojson = function(results, matchList){
	var count = 1,
	nodeList = [],
	edgeList = [],
	singleList = [],
	nidList = [],
	eidList = [],
	index,
	typeMap = {

		"Statute" 		: '#00639e',
		"CFR"	  		: '#7bbf6a',
		"USC"			: "#fc3147",
		"Warms"			: "#f29f00",
		"Public Law"	: "#191919",
		"pl"			: "#191919",
		"HR"			: "#104e8b",
		"statute" 		: '#00639e',
		"stat" 			: '#00639e',
		"cfr"	  		: '#7bbf6a',
		"usc"			: "#fc3147",
		"warms"			: "#f29f00",
		"public law"	: "#191919"
	};
	results.forEach(function(p){
		var no1 = {
			"l1"		: p['n_l1'],
			"l2"		: parseInt(p['n_l2']),
			"l3"		: parseInt(p['n_l3']),
			"name"		: p['n_name'],
			"url"		: p['n_url'],
			"color"		: typeMap[p['n_l1']],
			"id"		: p['n_id'].toString(),
			"id_num"	: p['n_id'],
			"edges"		: [],
			"matchQuery" : matchList === [] ? true : _.includes(matchList, p['n_id'])
		};
		if (p['m_id'] !== null){
			var no2 = {
				"l1"		: p['m_l1'],
				"l2"		: parseInt(p['m_l2']),
				"l3"		: parseInt(p['m_l3']),
				"name"		: p['m_name'],
				"url"		: p['m_url'],
				"color"		: typeMap[p['m_l1']],
				"id"		: p['m_id'].toString(),
				"id_num"	: p['m_id'],
				"edges"		: [],
				"matchQuery" : matchList === [] ? false : _.includes(matchList, p['m_id'])
			};

			var edge = {
				"source" 	: (_.startsWith(p['r_target'], no1.url) ? p['m_id'] : p['n_id']).toString(),
				"target" 	: (_.startsWith(p['r_target'], no1.url) ? p['n_id'] : p['m_id']).toString(),
				"id"	 	: count.toString(),
				'size'	 	: 50,
				// 'context'	: p.r._data.data.context,
				// 'label'  	: p.r._data.type,
				'color'	 	: '#ccc',
				'type'		: "arrow",
				'citation_exp' 	: p['r_context'] ? edgeType(p['r_context'],count) : p['r_type'],//(count % 5).toString()//p['r_type']//p['n_l2']
				'citation_hlt'	: p['r_type'] ? p['r_type'] : "Generic"
			};
			if(nidList.indexOf(no1.id) === -1){
				no1.edges.push({edge: count, type: (_.startsWith(p['r_target'], no1.url) ? "target" : "source")});
				nodeList.push(no1);
				nidList.push(no1.id);
			} else {
				index = nidList.indexOf(no1.id);
				nodeList[index].edges.push({edge: count, type: (_.startsWith(p['r_target'], no1.url) ? "target" : "source")});
				nodeList[index].matchQuery = nodeList[index].matchQuery || no1.matchQuery;
			}

			if(nidList.indexOf(no2.id) === -1){
				no2.edges.push({edge: count, type: (_.startsWith(p['r_target'], no2.url) ? "target" : "source")})
				nodeList.push(no2);
				nidList.push(no2.id);
			} else {
				index = nidList.indexOf(no2.id);
				nodeList[index].edges.push({edge: count, type: (_.startsWith(p['r_target'], no2.url) ? "target" : "source")});
				nodeList[index].matchQuery = nodeList[index].matchQuery || no2.matchQuery;
			}

			if(eidList.indexOf(edge.url) === -1){
				edgeList.push(edge);
			}

			count++;
		} else {
			singleList.push(no1);
		}

	})
	return {nodes : nodeList,
			edges : edgeList,
			singletons: singleList};
}

var edgeType = function(context,id){
	var testStrs = {"amend": "Amended",
					"authoriz": "Authorized",
					"defin": "Defined",
					"requir": "Required" };
	var edgeType = null;
	_.keys(testStrs).forEach(function(r){
		if ((new RegExp(r)).test(context)){
			edgeType = testStrs[r];
		}
	})
	return edgeType ? edgeType : "Generic";
}

var grainParser = function(grain){
	switch(grain) {
		case 'Act':
			return "Vacaa1";
		case 'Title':
			return "Vacaa2";
		case 'Section':
			return "Vacaa3";
		default:
			return grain;
	}
}

var childSpawn = function(exe, args, fun){
	return new promise(function(resolve, reject){
		try {
			var child = spawn(exe, args, {cwd: __dirname});
			var out = "";
			child.stdout.on('data',function(data){
				try {
					data = String.fromCharCode.apply(null, data)
					if(data.match(/^ready/)){
						var data = data.split(":")
						var port = parseInt(data[1]);
						info("java listening on port " + port)
						var client = net.connect(port);
						fun(client);
					} else {
						out += data;
					}
				} catch (e){
					error("name: " + e.name + "\nmessage: " + e.message + "\nstack: " + e.stack);
					reject(e);
				}
			})
			child.stderr.on('data',function(data){
				error('java stderr: ' + data);
				reject();
			});
			child.on('error',function(code){
				error('java error: ' + code);
				reject(code);
			})
				 .on('close', function(code){
				 	if (code === 0){
				 		resolve(out);
				 	} else {
				 		reject("unknown error, code " + code);
				 	}
				 })
		} catch (e){
			error("name: " + e.name + "\nmessage: " + e.message + "\nstack: " + e.stack);
			reject(e);
		}
	})
}

var generateRandomString = function(len){
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for (var i = 0; i < len; i++){
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }

    return text;
}


var xml_text = function(xml_str){
	return  new xmldom.DOMParser().parseFromString(xml_str).documentElement.textContent.replace(/( +\n)/gm,"").replace(/\)\n +/gm,") ").replace(/\(\n +/gm,"(");
};

var xml_str = function(xml){
	return  pd.xml(new xmldom.XMLSerializer().serializeToString(xml).replace(/(\\n|\n|\r|\t)/gm, "").replace(/ </gm,"<"));
};

var process_xml = function(xml){
	var xml2 = xml.replace(/(\\n|\n|\r|\t)/gm, "").replace(/> +</gm,"><");
	var out =  new xmldom.DOMParser().parseFromString(xml2);
	return out;
}

var error = function(str,emit){
	str = typeof(str) === "string" ? str : JSON.stringify(str);
	if (emit) {
		global.emitter.emit("message", str);
	}
	console.log(chalk.red(str));
}
var success = function(str,emit){
	str = typeof(str) === "string" ? str : JSON.stringify(str);
	if (emit) {
		global.emitter.emit("message", str);
	}
	console.log(chalk.green(str));
}
var warning = function(str,emit){
	str = typeof(str) === "string" ? str : JSON.stringify(str);
	if (emit) {
		global.emitter.emit("message", str);
	}
	console.log(chalk.yellow(str));
}
var info = function(str,emit){
	str = typeof(str) === "string" ? str : JSON.stringify(str);
	if (emit) {
		global.emitter.emit("message", str);
	}
	console.log(chalk.cyan(str));
}

module.exports = {
	neo4jtojson: neo4jtojson,
	grainParser: grainParser,
	childSpawn: childSpawn,
	generateRandomString: generateRandomString,
	java_layout: java_layout,
	combine_output: combine_output,
	error: error,
	success: success,
	warning: warning,
	info: info,
	xml_text: xml_text,
	xml_str: xml_str,
	process_xml: process_xml
}

