/*jshint newcap: false */
/*jshint -W069 */
/*globals sigma, d3, d3pie, $, sprintf */
(function() {
	'use strict';

	angular
	.module('policynet')
	.factory('graph', graph);

	/** @ngInject */
	function graph($log, $mdSidenav, $compile, query, toastr) {
		var sigmaSettings = {
			labelAlignment: "top",
			edgeLabelSize: 'proportional',
			nodeLabelSize: 'proportional',
			labelSizeRatio : 2,
			edgeLabelThreshold: 2.5,
			LabelThreshold: 6,
			autoScale: true,
			minNodeSize: 0,
			maxNodeSize: 0,
			minEdgeSize: 0,
			maxEdgeSize: 0,
			animationsTime: 2000,
			enableEdgeHovering : true,
			edgeHoverColor : "default",
			edgeHoverSizeRatio : 2,
			defaultEdgeHoverColor : '#ee7621',
			edgesPowRatio: 0.5,
			nodesPowRatio: 0.5,
            sideMargin: 0.5,
		};

		var graphSettings = {
			highlightColor: "#2ca25f",
			nonHighlightColor: "rgba(0,0,0,0.1)"
		};
		var colorscale = d3.scale.category10();

		function drawNetwork(scope, context){
			context = context || scope.mainContext;
			var graphdata = scope.graph[context].data;

			var sigmaLayout = !graphdata.nodes[0].x;
			if (!$.isEmptyObject(scope.graph[context].obj)){scope.graph[context].obj.graph.clear();}
			var sigmaSettings_instance = _.clone(sigmaSettings);

			var edgeSize = Math.max(1,Math.min(4, 5 - Math.log(graphdata.edges.length)/Math.log(10)));
			graphdata.edges.forEach(function(e){
				e.size = edgeSize;
			});
			var nodeSize = Math.max(1,Math.min(5, 6 - Math.log(graphdata.nodes.length)/Math.log(10)));
			graphdata.nodes.forEach(function(e){
				e.size = nodeSize;
			});

			graphdata.nodes.forEach(function(d, i, a){
				if (sigmaLayout){
					d.x = Math.cos(Math.PI * 2 * i / a.length);
					d.y = Math.sin(Math.PI * 2 * i / a.length);
				}
				d.label = d.id_num ? (_.includes(['usc', 'cfr'], d.l1) ? d.l2 + " " + d.l1.toUpperCase() + " " + d.l3 + ": " + d.name : d.name).replace("� ", "") : "";
				if(d.matchQuery){
					// use image
					// d.image = {
					// 	url: "/assets/img/node-image.png",
					// 	scale: 2,
					// 	clip: 1
					// }
					// d.size = d.size * 2;


					// use star
					d.type = 'star';
					d.star = {numPoints: 5, innerRatio: 2};
					d.size = d.size * 1.5;
				}
			});
			var container = scope.graph[context].container;
			$("#"+container).parent().css("padding-bottom",Math.max(50, 100 * graphdata.layout.overallY / graphdata.layout.overallX)+"%");
			var s = new sigma({
				graph: graphdata,
				renderer: {
					container: container,
					type: 'canvas'
				},
				settings: sigmaSettings_instance
			});

			s.camera.goTo({
				x: 0,
				y: 0,
				angle: 0,
				ratio: 1
			});

			scope.graph[context].tooltipInstance = sigma.plugins.tooltips(
				s,
				s.renderers[0],
				{ node: {
						template: '<div class="contextual-menu-wrapper md-whiteframe-z2 md-default-theme">' +
									'<md-menu-content width="4">' +
										'<md-menu-item>' +
											'<button class="md-button md-default-theme" ng-click="getNodeInformation(tootip_context.node)" tabindex="0"><span class="ng-scope">' +
												'Get Node Information' +
											'</span><div class="md-ripple-container"></div></button>' +
										'</md-menu-item>' +
										'<md-menu-item aria-hidden="false" class="">' +
											'<button class="md-button md-default-theme" ng-click="getLocalGraph(tootip_context.node)" tabindex="0"><span class="ng-scope">' +
												'Get Local Graph' +
											'</span></button>' +
										'</md-menu-item>' +
									'</md-menu-content>' +
								'</div>',
						renderer: function(node, template){
							scope.tootip_context.node = node;
							return $compile(template)(scope)[0];
						}

					}
				}
				);
			s.refresh();
			scope.graph[context].obj = s;
			if (sigmaLayout){
				sigma.layouts.fruchtermanReingold.start(s, {
					autoArea: false,
					area: 1000000 * scope.graph[context].data.edges.length,
					gravity: 1,
					speed: 0.1,
					iterations: 1000
				});
			}
		}

		function getNodeInformation(node, scope) {
			var context = scope.mainContext;
			if (scope.graph[context] && scope.graph[context].tooltipInstance){
				scope.graph[context].tooltipInstance.close();
			}
			// var edges = scope.graph[context].obj.graph.edges.call();
			// scope.graph[context].edge.text = edges.filter(function(d){return (node.id === d.target) })[0]
			if (scope.graph[context].refContext && !node.matchQuery) {
				var sourceid = [];
				node.edges.forEach(function(e){
					sourceid.push(scope.graph[context].data.edges[e.edge-1].source);
				});
				query.get("vacaanode", {
					node1id: node.id,
					node2id: sourceid.join(",")
				}, true).then(function(data){
					scope.graph[context].edge = [];
					data.forEach(function(d){
						scope.graph[context].edge.push({
							type: d.r.type,
							context: d.r.properties.context,
							to: d["m.name"]
						});
					});
					data[0].n.properties.text = data[0].n.properties.text.replace(/\\n/g,"\n\n");
					scope.graph[context].node = data[0].n.properties;
					scope.$emit('loading',false);
					$mdSidenav("right").toggle();
				});
			} else {
				query.get("node", {
					nodeid: node.id
				}, true).then(function(data){
					data[0].n.properties.text = data[0].n.properties.text.replace(/\\n/g,"\n\n");
					scope.graph[context].node = data[0].n.properties;
					scope.$emit('loading',false);
					$mdSidenav("right").toggle();
				});
			}
		}

		function getGraphSections(graphdata, l1, includeLinked){

			var sections = {},
				section_label,
				ctr = 0;

			graphdata.nodes.forEach(function(e){
				if (e.name){
					var includeInCount = e.name && ((!includeLinked && e.matchQuery) || includeLinked) ? 1 : 0;
					if (e.l1 === l1){ // for nodes in the same corpus
						section_label = e.l1 + " " + e.l2; // corpus/title
						if (sections[section_label]) {
							sections[section_label].value += includeInCount;
						} else {
							sections[section_label] = {label: section_label, value: includeInCount, color: colorscale(ctr)};
							ctr++;
						}
					} else {
						section_label = e.l1;
						if (sections[section_label]) {
							sections[section_label].value += includeInCount;
						} else {
							sections[section_label] = {label: section_label, value: includeInCount, color: colorscale(ctr)};
							ctr++;
						}
					}
					e.color = sections[section_label].color;
				}
			});
			return _.filter(_.values(sections), function(n){return n.value > 0;});
		}

		function getEdgeTypes(graphdata, refSource){
			var types = {},
				type_label,
				ctr = 0;

			graphdata.edges.forEach(function(e){
				type_label = e["citation_"+refSource];
				if (types[type_label]) {
					types[type_label].value ++;
				} else {
					types[type_label] = {label: type_label, value: 1, color: colorscale(ctr)};
					ctr ++;
				}
			});
			return _.values(types);
		}

		function getEdgeWeight(graphdata){
			var types = {},
				type_label,
				ctr = 0;

			graphdata.edges.forEach(function(e){
				type_label = e.count.toString();
				if (types[type_label]) {
					types[type_label].value ++;
				} else {
					types[type_label] = {label: type_label, value: 1, color: colorscale(ctr)};
					ctr ++;
				}
			});
			return _.values(types);
		}

		function highlightNode(scope,val,color,groupedData, context){
			var includeLinked = (scope.graph[context].pieShow[0] === 'Matched & Linked' ? true : false);
			scope.graph[context].pie_members[0] = groupedData ? _.map(groupedData, function(g){return g.label;}).sort(function(a,b){
					a = a.split(" ");
					b = b.split(" ");
					if (a[0] !== b[0]){
						return a[0] > b[0] ? 1 : -1;
					} else {
						return parseInt(a[1]) - parseInt(b[1]);
					}
				}) : "";
			scope.graph[context].data.nodes.forEach(function(e){
				if (e.name){
					if (!e.color_orig){
						e.color_orig = e.color;
					}
					if (typeof(val) === "string" && ((!includeLinked && e.matchQuery) || includeLinked)){
						if (groupedData){
							e.color = _.includes(scope.graph[context].pie_members[0],e.l1) || _.includes(scope.graph[context].pie_members[0],e.l1 + " " + e.l2) ? color : graphSettings.nonHighlightColor;
						} else {
							e.color = (e.l1 === val || e.l1 + " " + e.l2 === val) ? color : graphSettings.nonHighlightColor;
						}
					} else if(typeof(val) === "string") {
						e.color = graphSettings.nonHighlightColor;
					} else {
						e.color = e.color_orig;
					}
				}
			});
			scope.$apply();
		}

		function highlightEdge(scope,val,color, groupedData, context){
			var refSource = (scope.graph[context].pieShow[1] === 'Experimental' ? 'exp' : 'hlt');
			scope.graph[context].pie_members[1] = groupedData ? _.map(groupedData, function(g){return g.label;}) : "";
			scope.graph[context].data.edges.forEach(function(e){
				if (!e.color_orig){
					e.color_orig = e.color;
				}
				if (typeof(val) === "string"){
					if (groupedData){
						e.color = _.includes(scope.graph[context].pie_members[1],e["citation_"+refSource]) ? color : graphSettings.nonHighlightColor;
					} else {
						e.color = (e["citation_"+refSource] === val) ? color : graphSettings.nonHighlightColor;
					}
				} else {
					e.color = e.color_orig;
				}
			});
			scope.$apply();
		}

		function highlightEdgeWeight(scope,val,color, groupedData, context){
			scope.graph[context].pie_members[2] = groupedData ? _.map(groupedData, function(g){return g.label;}) : "";
			scope.graph[context].data.edges.forEach(function(e){
				if (!e.color_orig){
					e.color_orig = e.color;
				}
				if (typeof(val) === "string"){
					if (groupedData){
						e.color = _.includes(scope.graph[context].pie_members[1],e.count.toString()) ? color : graphSettings.nonHighlightColor;
					} else {
						e.color = (e.count.toString() === val) ? color : graphSettings.nonHighlightColor;
					}
				} else {
					e.color = e.color_orig;
				}
			});
			scope.$apply();
		}

		function pieToggle(n, scope){
			var context = scope.mainContext;
			if (n === 0){
				scope.graph[context].pie[0].destroy();
				scope.graph[context].pie[0] = null;
				drawPieTitle(scope, context);
			} else {
				scope.graph[context].pie[1].destroy();
				scope.graph[context].pie[1] = null;
				drawPieCitation(scope, context);
			}
		}

		function drawPieTitle(scope, context){
			context = context || scope.mainContext;
			if ($("#" + scope.graph[context].pieTitle).length === 0) {return;}
			var graphdata = scope.graph[context].data;
			var includeLinked = (scope.graph[context].pieShow[0] === 'Matched & Linked' ? true : false);
			scope.graph[context].pie[0] = drawPie(scope.graph[context].pieTitle, "Title", getGraphSections(graphdata, scope.network_query.l1, includeLinked), true, function(e){
				if(!e.expanded) {
					highlightNode(scope,e.data.label,e.data.color,e.data.groupedData, context);
				} else if(e.expanded) {
					highlightNode(scope,null,null,null,context);
				}
				scope.graph[context].obj.refresh();
			});
		}

		function drawPieCitation(scope, context){
			context = context || scope.mainContext;
			if ($("#" + scope.graph[context].pieCitation).length === 0) {return;}
			var graphdata = scope.graph[context].data;
			var refSource = (scope.graph[context].pieShow[1] === 'Experimental' ? 'exp' : 'hlt');
			scope.graph[context].pie[1] = drawPie(scope.graph[context].pieCitation, "Citation", getEdgeTypes(graphdata, refSource), true, function(e){
				if(!e.expanded) {
					highlightEdge(scope,e.data.label,e.data.color,e.data.groupedData, context);
				} else if(e.expanded) {
					highlightEdge(scope,null,null,null,context);
				}
				scope.graph[context].obj.refresh();
			});
		}

		function drawPieEdgeWeight(scope, context){
			context = context || scope.mainContext;
			if ($("#" + scope.graph[context].pieCitation).length === 0) {return;}
			clearGraph(scope, "pie");
			var graphdata = scope.graph[context].data;
			scope.graph[context].pie[2] = drawPie(scope.graph[context].pieCitation, "Co-Occurrences Count", getEdgeWeight(graphdata), false, function(e){
				if(!e.expanded) {
					highlightEdgeWeight(scope,e.data.label,e.data.color,e.data.groupedData, context);
				} else if(e.expanded) {
					highlightEdgeWeight(scope,null,null,null,context);
				}
				scope.graph[context].obj.refresh();
			});
		}

		function drawPie(container, title, data, smallSegmentGrouping, onClickSegment){
			return new d3pie(container, {
				header: {
					title: {
						text: title,
						fontSize: 24
					},
				},
				size: {
					canvasHeight: $("#" + container).closest("div").width() * 0.9,
					canvasWidth: $("#" + container).closest("div").width() * 0.9,
					pieInnerRadius: "30%",
					pieOuterRadius: "70%"
				},
				data: {
					sortOrder: "value-asc",
					smallSegmentGrouping: {
						enabled: smallSegmentGrouping,
						value: 2,
						valueType: "percentage",
						label: "other",
						color: "#000000"
					},
					content: data,
				},
				labels: {
					outer: {
						format: "label",
						pieDistance: 25
					},
					inner: {
						format: "value"
					},
					mainLabel: {
						fontSize: 12
					},
					percentage: {
						color: "#999999",
						fontSize: 12,
						decimalPlaces: 0
					},
					value: {
						color: "#ffffff",
						fontSize: 11
					},
					lines: {
						enabled: true,
						style: "curved",
						color: "#cccccc"
					}
				},
				effects: {
					pullOutSegmentOnClick: {
						effect: "linear",
						speed: 400,
						size: 8
					}
				},
				callbacks: {
					onClickSegment: onClickSegment
				},
				misc: {
					gradient: {
						enabled: false,
						percentage: 100
					},
					canvasPadding: {
						top: 0,
						right: 0,
						bottom: 0,
						left: 0
					}
				}
			});
		}

		function clearGraph(scope, context){
			if (scope.table_query){
				scope.table_query.page = 1;
			}
			for (var context2 in scope.graph) {
				if (scope.graph.hasOwnProperty(context2) && scope.graph[context2].pie) {
					scope.graph[context2].pie.forEach(function(pie){
						pie.element.innerHTML="";
					});
					scope.graph[context2].pie = [];
					scope.graph[context2].pie_members = [];
				}
			}
			if(context === "pie"){
			} else if(context){
				if (!$.isEmptyObject(scope.graph[context].obj)){
					scope.graph[context].obj.graph.clear();
					scope.graph[context].tooltipInstance.close();
					sigma.plugins.killTooltips(scope.graph[context].obj);
					scope.graph[context].data = null;
					if (scope.graph[context].edge) {
						scope.graph[context].edge = null;
					}
					scope.graph[context].statistics = {};
					$("#" + scope.graph[context].container + " canvas").remove();
				}
			} else {
				scope.mainView = scope.mainView_default;
				scope.sideView = scope.sideView_default;
				for (context in scope.graph) {
					if (scope.graph.hasOwnProperty(context) && !$.isEmptyObject(scope.graph[context].obj)) {
						scope.graph[context].obj.graph.clear();
						scope.graph[context].tooltipInstance.close();
						sigma.plugins.killTooltips(scope.graph[context].obj);
						scope.graph[context].data = null;
						if (scope.graph[context].edge) {
							scope.graph[context].edge = null;
						}
						scope.graph[context].statistics = {};
						$("#" + scope.graph[context].container + " canvas").remove();
					}
				}
			}
		}

		function changeView(context, scope){ //change view without changing model, i.e., when data already exist. if data doesn't exist or need to be changed, use draw functions instead
			scope.mainView = context;
			scope.sideView = scope.sideView_default;
			if (context !== "table"){
				scope.mainContext = context;
				clearGraph(scope, "pie");
				if (scope.graph[context].pieShow[0]){
					drawPieTitle(scope,context);
				}
				if (scope.graph[context].pieShow[1]){
					drawPieCitation(scope,context);
				}
			}
		}

		function draw(scope, network, pieTitle, pieCitation, data){
			var context = scope.mainContext;
			if (data.singletons){
				data.nodes_combined = _.filter(data.nodes.concat(data.singletons), function(node){return !!node.name;});
			} else {
				data.nodes_combined = data.nodes;
			}

			if (data.java){
				scope.graph[context].statistics["Average Degree"] = data.java.averageDegree.toFixed(3);
				scope.graph[context].statistics["Weighted Average Degree"] = data.java.weightedAverageDegree.toFixed(3);
				scope.graph[context].statistics["Edges"] = data.java.edges;
				scope.graph[context].statistics["Nodes"] = data.java.nodes;
				scope.graph[context].statistics["Singletons"] = data.singletons.length;
			}

			scope.graph[context].data = data;
			if (pieTitle){
				drawPieTitle(scope);
			}
			if (pieCitation){
				drawPieCitation(scope);
			}
			if (network){
				drawNetwork(scope);
			}
			scope.$emit('loading',false);
		}

		function table(scope, data){
			var context = scope.mainContext;
			data.nodes_combined = data.nodes;
			scope.graph[context].statistics["Matched Nodes"] = data.nodes_combined.length;
			_.forEach(data.statistics, function(n, key){
				scope.graph[context].statistics[key] = n;
			});
			scope.graph[context].data = data;
			scope.$emit('loading',false);
		}



		function downloadGraph(scope, context){
			context = context || scope.mainContext;
			scope.canvas_href = $("#" + scope.graph[context].container + " .sigma-scene")[0].toDataURL('image/png').replace(/^data:image\/[^;]*/,'data:application/octet-stream');
		}

		function downloadGraphData(scope, context){
			context = context || scope.mainContext;
			var output = _.clone(scope.graph[context].data);
			output.nodes = output.nodes_combined;
			output = _.omit(output, ['singletons', 'java', 'nodes_combined']);
			var outputString = 'data:text/json;charset=utf8,' + encodeURIComponent(JSON.stringify(output));
			if (outputString.length < 2000000) {
				scope.graph_data = outputString;
			} else {
				toastr.error("Sorry, the file is too large to download.");
			}
		}

		function downloadTableData(scope, context){
			context = context || scope.mainContext;
			var output = '"Node ID","Text","Title","Section","Node Name","Degree","Matched"\n';
			scope.graph[context].data.nodes_combined.forEach(function(n){
				output += sprintf('%s,"%s",%s,%s,"%s",%s,"%s"\n',n.id,n.l1,n.l2,n.l3 ? n.l3 : "",n.name.replace(/"/g,'""'),n.edges.length,n.matchQuery? "Matched" : "Linked");
			});
			var outputString = 'data:text/json;charset=utf8,' + encodeURIComponent(output);
			if (outputString.length < 2000000) {
				scope.table_data = outputString;
			} else {
				toastr.error("Sorry, the file is too large to download.");
			}
		}

		return {
			draw: draw,
			table: table,
			drawPieEdgeWeight: drawPieEdgeWeight,
			changeView: changeView,
			clearGraph: clearGraph,
			downloadGraph: downloadGraph,
			getNodeInformation: getNodeInformation,
			pieToggle: pieToggle,
			downloadGraphData: downloadGraphData,
			downloadTableData: downloadTableData
		};
	}
})();
