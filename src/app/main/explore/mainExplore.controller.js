/*globals console */
(function() {
	'use strict';

	angular
	.module('policynet')
	.controller('mainExploreController', mainExploreController);

	/** @ngInject */
	function mainExploreController($scope, $sce, query, graph) {

		$scope.clearGraph = function(context){graph.clearGraph($scope, context);};
		$scope.downloadGraph = function(){graph.downloadGraph($scope);};
		$scope.downloadGraphData = function(){graph.downloadGraphData($scope);};
		$scope.downloadTableData = function(){graph.downloadTableData($scope);};
		$scope.getNodeInformation = function(node){graph.getNodeInformation(node, $scope);};
		$scope.pieToggle = function(n){graph.pieToggle(n, $scope);};
		$scope.changeView = function(context){graph.changeView(context, $scope);};
		$scope._ = _;

		$scope.page = "explore";
		$scope.description = "Welcome to the main search page. Eventually this will allow you to search the United States Code (USC), the Code of Federal Regulations (CFR) as well as various public laws and agency specific documents. For now you can search either the entire USC or specific sections for topics of interest. Moving the slider allows you to return more or less results.";
		$scope.graph = {
			global: {
				data  				: null,
				obj   				: {},
				pie   				: [],
				pie_members			: [],
				container			: $scope.page + "Container",
				pieTitle			: $scope.page + "PieTitleContainer",
				pieCitation			: $scope.page + "PieCitationContainer",
				pieShow				: ['Matched & Linked', 'Experimental'],
				statistics			: {}
			},
			local: {
				data  				: null,
				obj   				: {},
				pie   				: [],
				pie_members			: [],
				container			: $scope.page + "Container_local",
				pieTitle			: $scope.page + "PieTitleContainer",
				pieCitation			: $scope.page + "PieCitationContainer",
				pieShow				: ['Matched & Linked', 'Experimental'],
				statistics			: {}
			}

		};
		$scope.lastAction = "";
		$scope.mainView_default = "global";
		$scope.sideView_default = "pie";
		$scope.mainView = $scope.mainView_default;
		$scope.mainContext = $scope.mainView_default;
		$scope.sideView = $scope.sideView_default;
		$scope.options = {
			l1				: ["All","usc","cfr"],
			l2				: ["All"],
		};

		$scope.network_query = {
			l1				: $scope.options.l1[0],
			l2				: $scope.options.l2[0],
			query			: '',
			limit			: 100
		};

		$scope.$watch('network_query.l1', function(nv){
			if ($scope.network_query.l1 === "All"){
				$scope.options.l2 = ["All"];
			} else {
				query.get("sections",{
					query: nv
				}, true).then(function(data){
					$scope.options.l2 = ["All"].concat(data);
					$scope.$emit('loading',false);
				});
			}
		});
		$scope.drawActions = [{
				name: "Relational Graph View",
				action: "standardView"
			},{
				name: "Matched Document Table",
				action: "tableStats"
			}];
		var start, end;
		$scope.tootip_context = {};
		$scope.getLocalGraph = function(node){
			var context = $scope.mainContext;
			if ($scope.graph[context].tooltipInstance){
				$scope.graph[context].tooltipInstance.close();
			}
			$scope.clearGraph('local');
			$scope.mainView = "local";
			$scope.mainContext = "local";
			start = new Date().getTime();
			query.get('neighborhood', {
				node: node.id,
				hop: 1
			}, true).then(function(data){
				graph.draw($scope, true, true, true, data);
				end = new Date().getTime();
				console.log("overall time: " + (end - start)/1000 + " s.");
			}, function(){
				$scope.$emit('loading',false);
			});
		};

		$scope.getData = function(action){
			var context = $scope.mainContext;
			if ($scope.graph[context].tooltipInstance){
				$scope.graph[context].tooltipInstance.close();
			}
			$scope.clearGraph('global');
			$scope.mainView = "global";
			$scope.sideView = $scope.sideView_default;
			$scope.mainContext = "global";
			start = new Date().getTime();
			$scope.lastAction = action;

			switch(action){
				case "standardView":

					query.get('network', {
						l1: $scope.network_query.l1,
						l2: $scope.network_query.l2,
						query: $scope.network_query.query,
						limit: $scope.network_query.limit
					}, true).then(function(data){
						graph.draw($scope, true, true, true, data);
						end = new Date().getTime();
						console.log("overall time: " + (end - start)/1000 + " s.");
					}, function(){
						$scope.$emit('loading',false);
					});
					break;

				case "tableStats":
					query.get('table_stats', {
						l1: $scope.network_query.l1,
						l2: $scope.network_query.l2,
						query: $scope.network_query.query,
						limit: $scope.network_query.limit
					}, true).then(function(data){
						$scope.mainView = 'table';
						$scope.sideView = 'stat';
						graph.table($scope, data);
						end = new Date().getTime();
						console.log("overall time: " + (end - start)/1000 + " s.");
					}, function(){
						$scope.$emit('loading',false);
					});
					break;
			}

		};


		$scope.selected = [];

		$scope.table_query = {
			filter: '',
			order: 'id_num',
			limit: 10,
			page: 1,
			itemPerPage: [10, 20, 50, 100]
		};

		$scope.onChangeOrder = function(order){
			$scope.table_query.order = order;
		};
	}
})();
