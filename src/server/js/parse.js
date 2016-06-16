var pd 				= require('pretty-data').pd,
	xmldom			= require('xmldom'),
	_				= require('lodash'),
	citation		= require('citation'),
	promise			= require('promise'),
	utils			= require('./utils.js'),
	query_utils		= require('./query.utils.js');



var redline = function(xml){
	var out = [];
	var prettyxml = pd.xml(xml);
	var doc = new xmldom.DOMParser().parseFromString(xml.replace(/(\n|\r|\t)/gm, "").replace(/> +</gm,"><"));
	var levels = ["section","subsection","paragraph","subparagraph","clause"];
	var quote_discard = ["term", "terms", "and", "the", "an", "a", "to", "of", "as", "entitled", "statement", "establishing"];
	// block to testing various things.
	// _.forEach(doc.getElementsByTagName('text'), function(n){
	// 	// if (!getChildrenByTag(quote.parentNode.parentNode, 'text').length && quote.parentNode.tagName !== 'quote'){
	// 	// 	console.log('Yes, i mean No!');
	// 	// 	console.log(quote.textContent);
	// 	// }
	// 	var cnt = getChildrenByTag(n.parentNode, 'text').length;
	// 	if (cnt > 1){
	// 		console.log(cnt);
	// 	}
	// })

	process_level(null, 'section', []); // recursively look for quoted-block and store information in the 'out' variable. although looking at this line it's not immediately obvious 'out' is the output variable

	var refs = [];
	var ref_promises = _.uniq(_.filter(out, function(change){
		return change.citation || change.action_cite !== 'same';
	}).map(function(change){
		return change.citation || change.action_cite;
	})).map(function(ref){
		return citationInDB(ref).then(function(result){
			return new promise(function(resolve, reject){
				if (result){
					refs.push(ref);
				}
				resolve();
			})
		})
	});
	return promise.all(ref_promises).then(function(){
		try{
			out.forEach(function(change){
				if ((change.citation && _.includes(refs, change.citation)) || (change.action_cite !== "same" && _.includes(refs, change.action_cite))) {
					change.citationExists = true;
				}
				change.ref = change.citation || (change.action_cite !== "same" && change.action_cite !== "" ? change.action_cite : "");
				if (change.ref !== ""){
					change.ref_link = getCitationLink(change.ref);
				}
			})

			// testing block
			// console.log(_.reduce(out, function(total, o){
			// 	if (!o.citation && (o.action_cite === "same" || o.action_cite === "")){
			// 		total ++;
			// 	}
			// 	return total;
			// }, '0'));

			return out.sort(function(a,b){
				return a.num.join(" ").localeCompare(b.num.join(" "));
			});
		} catch (err){
			utils.error("err");
			utils.error(err.stack);
		}
	})

	function process_level(node, thisLvl, secNum){
		// on 1st iteration, get all the sections, on subsequent iteration, get all next levels
		if (node === null){
			_.forEach(doc.getElementsByTagName(thisLvl), process_level_node);
		} else {
			get_next_level(node).forEach(process_level_node);
		}

		function process_level_node(node){
			if (node.getElementsByTagName('quoted-block').length + node.getElementsByTagName('quote').length > 0){

				var nextSecNum = secNum.concat([node.getElementsByTagName('enum')[0].textContent]);
				has_text = !!getChildrenByTag(node, "text").length;
				if (has_text){
					out = out.concat(get_changes(node, nextSecNum));
				} else {
					var ind = levels.indexOf(node.tagName);
					if (ind < levels.length - 1){
						process_level(node, levels[ind + 1], nextSecNum);
					} else {
						utils.error(node.tagName + ' still has no text');
						utils.error(nextSecNum);
					}
				}
			}
		}
	}


	function get_next_level(node){
		var tf = true,
			children = [],
			thisLvl = node.tagName;
		while (tf){
			thisLvl = levels[levels.indexOf(thisLvl) + 1];
			children = getChildrenByTag(node, thisLvl);
			tf = !children.length && thisLvl;
		}
		return children;
	}

	function get_changes(sec, num){

		var tag = sec.tagName,
			out = [],
			texts = getChildrenByTag(sec, "text"),
			ref = getCitation(texts[0]),
			sec_xml = utils.xml_str(sec),
			sec_text = utils.xml_text(sec_xml);

		if (texts.length > 1){
			utils.error("more than 1 text elements");
			utils.error(texts[0].textContent);
		}

		recurse_changes_qb(sec.cloneNode(true));
		recurse_changes_q(sec.cloneNode(true));

		function recurse_changes_qb(sec){
			var qbs = getChildrenByTag(sec, 'quoted-block')
			if (qbs.length){
				get_changes_qb(qbs);
			} else if (sec.getElementsByTagName('quoted-block').length){
				get_next_level(sec).forEach(function(node){
					recurse_changes_qb(node);
				})
			}
		}

		function recurse_changes_q(sec){
			var text = getChildrenByTag(sec, 'text');
			if (text.length && getChildrenByTag(text[0], 'quote').length){
				get_changes_q(getChildrenByTag(text[0], 'quote'));
			} else if (sec.getElementsByTagName('quote').length){
				get_next_level(sec).forEach(function(node){
					recurse_changes_q(node);
				})
			}
		}


		// get quote stuff
		function get_changes_q(qs){

			qs.forEach(function(q){
				var	change_xml = utils.xml_str(q),
					change_text = utils.xml_text(change_xml),
					action_text = q.previousSibling.textContent,
					action_xml = utils.xml_str(q.parentNode),
					action_cite = getCitation(q.parentNode);

				var parent = q.parentNode;
					secNumRev = [];
				while (parent.tagName !== tag){
					if (getChildrenByTag(parent, 'enum').length){
						secNumRev.push(getChildrenByTag(parent, 'enum')[0].textContent);
					}
					parent = parent.parentNode;
				}
				var qSecNum = num.concat(secNumRev.reverse());

				var change_quote = !_.includes(quote_discard, _.last(_.words(action_text)));

				out.push({
					"num": qSecNum,
					"tag_name": "quote",
					"sec_xml": sec_xml,
					"sec_text": sec_text,
					"change_text": change_text,
					"change_xml": change_xml,
					"action_text": action_text,
					"action_xml": action_xml,
					"action_cite": action_cite,
					"citation": ref,
					"change_quote": change_quote
				});
			});
		}

		// get quoted-block stuff
		function get_changes_qb(qbs){
			qbs.forEach(function(qb){
				qb.removeChild(qb.getElementsByTagName("after-quoted-block")[0]);
				_.forEach(qb.getElementsByTagName('enum'), function(v,k){
					v.textContent += " ";
				});
				_.forEach(qb.getElementsByTagName('header'), function(v,k){
					v.textContent += "\n";
				});
				_.forEach(qb.getElementsByTagName('text'), function(v,k){
					v.textContent += "\n";
				});

				var sib = qb.previousSibling,
				action_text, action_cite;
				if (sib.tagName === 'text'){
					action_text = sib.textContent;
					action_cite = action_text === texts[0].textContent ? "same" : getCitation(qb.previousSibling);
				}
				var parent = qb.parentNode;
					secNumRev = [];
				while (parent.tagName !== tag){
					if (getChildrenByTag(parent, 'enum').length){
						secNumRev.push(getChildrenByTag(parent, 'enum')[0].textContent);
					}
					parent = parent.parentNode;
				}
				var qbSecNum = num.concat(secNumRev.reverse());

				var	change_xml = utils.xml_str(qb),
					change_text = utils.xml_text(change_xml);

				out.push({
					"num": qbSecNum,
					"tag_name": "quoted-block",
					"sec_xml": sec_xml,
					"sec_text": sec_text,
					"change_text": change_text,
					"change_xml": change_xml,
					"action_text": action_text,
					"action_cite": action_cite,
					"citation": ref
				});
			});
		}
		return out;

	}

	function getCitation(textNode){
		// only get USC citation
		var ref = "",
			refs = _.filter(getChildrenByTag(textNode, 'external-xref'), function(el){
			return el.getAttribute('legal-doc') === 'usc';
		});

		if (refs.length > 1){
			utils.warning("more than 1 ref in text");
			utils.warning(textNode.textContent)
		} else if (refs.length ===1){
			ref = refs[0].getAttribute("parsable-cite");
		} else {
			citations = citation.find(textNode.textContent.replace(String.fromCharCode(8211), "-"), {types: "usc"}).citations;
			try {
				ref = citations.length ? citations[0].usc.id : "";
			} catch (err){
				utils.error(textNode.textContent);
				utils.error(citations)
				throw err
			}
		}
		return ref !== "" ? "/us/" + ref : "";
	}



	function getChildrenByTag(parent, tagname){
		return _.filter(parent.childNodes, function(child){
			return child.tagName === tagname;
		})
	}

}


var citationInDB = function(ref){

	ref_sec = ref.split('/').slice(0,5).join('/');
	var es_query = _.cloneDeep(query_utils.es_base_query);

	es_query.size = 1;
	es_query.body.query = {"bool": {"must": [{term: { url: ref_sec }}]}};

	return query_utils.query_elastic(es_query).then(function(results){
		return new promise(function(resolve,reject){
			resolve(!!results.hits.total);
		});
	})
}

var getCitationLink = function(ref){
	try{
	var cite = {
		title: ref.split('/')[3],
		section: ref.split('/')[4],
		subsections: ref.split('/').splice(5),
		id: ref.split('/').splice(1).join('/')
	}
	return citation.links.gpo.citations.usc(cite).landing;
}
catch(err){
	utils.error(err);
	utils.error(err.message);
	utils.error(err.stack)
}
}

module.exports = {
	redline: redline,
	citationInDB: citationInDB,
	getCitationLink: getCitationLink
}
