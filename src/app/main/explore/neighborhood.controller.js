/*globals console */
(function() {
	'use strict';

	angular
	.module('policynet')
	.controller('neighborhoodController', neighborhoodController);

	/** @ngInject */
	function neighborhoodController($scope, $sce, query, graph) {

		$scope.clearGraph = function(context){graph.clearGraph($scope, context);};
		$scope.downloadGraph = function(){graph.downloadGraph($scope);};
		$scope.downloadGraphData = function(){graph.downloadGraphData($scope);};
		$scope.downloadTableData = function(){graph.downloadTableData($scope);};
		$scope.getNodeInformation = function(node){graph.getNodeInformation(node, $scope);};
		$scope.pieToggle = function(n){graph.pieToggle(n, $scope);};
		$scope.changeView = function(context){graph.changeView(context, $scope);};
		$scope._ = _;

		$scope.page = "neighborhood";
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
			}

		};
		$scope.mainView_default = "global";
		$scope.sideView_default = "pie";
		$scope.mainView = $scope.mainView_default;
		$scope.mainContext = $scope.mainView_default;
		$scope.sideView = $scope.sideView_default;

		$scope.drawActions = [{
				name: "Relational Graph View",
				action: "standardView"
			}];
		$scope.network_query = {
			"hop": 1,
			"searchText": ""
		};
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
				hop: $scope.hop
			}, true).then(function(data){
				graph.draw($scope, true, true, true, data);
				end = new Date().getTime();
				console.log("overall time: " + (end - start)/1000 + " s.");
			}, function(){
				$scope.$emit('loading',false);
			});
		};

		$scope.getData = function(){
			var context = $scope.mainContext;
			if ($scope.graph[context].tooltipInstance){
				$scope.graph[context].tooltipInstance.close();
			}
			$scope.clearGraph('global');
			$scope.mainView = "global";
			$scope.mainContext = "global";
			start = new Date().getTime();

			query.get('neighborhood', {
				node: $scope.network_query.selectedItem.value,
				hop: $scope.network_query.hop
			}, true).then(function(data){
				graph.draw($scope, true, true, true, data);
				end = new Date().getTime();
				console.log("overall time: " + (end - start)/1000 + " s.");
			}, function(){
				$scope.$emit('loading',false);
			});
		};
		$scope.getSuggestions = function(prefix){
			return query.get('suggest', {
				field: "name",
				prefix: prefix,
				limit: 10
			}, false).then(function(data){
				var output = _.map(data.suggester[0].options, function(o){
					return {
						"display": o.text,
						"value": o.payload.id
					};
				});
				$scope.$emit('loading',false);
				return output;
			}, function(){
				$scope.$emit('loading',false);
			});
		};
	}
})();
