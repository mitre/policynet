(function() {
	'use strict';

	angular
	.module('policynet')
	.run(exposeState)
	.config(["$locationProvider", function($locationProvider) {
		$locationProvider.html5Mode({
			enabled: true,
			requireBase: false,
		});
	}])
	.config(routeConfig);


	/** @ngInject */
	function exposeState($rootScope, $state, $stateParams, $log, query){
		$rootScope.$state = $state;
		$rootScope.$stateParams = $stateParams;
		$rootScope.$on('$stateChangeSuccess', function(event, toState){
			query.get(['visit',toState.name], false).then(function(){
			}, function(err){
				$log.error(err);
			});
		});
		$rootScope.sections = [{
			name: 'Overview',
			type: 'toggle',
			pages: [{
				name: "Get the idea",
				url: '/intro',
				type: 'link',
				subheading: 'If you treat the law as a network, what insights can you gain?'
			},{
				name: "Play with the data",
				url: '/explore',
				type: 'link'
			},{
				name: "Get neighborhood",
				url: "/neighborhood",
				type: "link"
			},{
				name: "Bills",
				url: "/bills",
				type: "link"
			}]
		}];
	}

	/** @ngInject */
	function routeConfig($stateProvider, $urlRouterProvider) {
		$stateProvider
		.state('intro', {
			url: '/intro',
			templateUrl: 'app/main/static/intro.html'
		})
		.state('explore', {
			url: '/explore',
			templateUrl: 'app/main/explore/explore.template.html',
			controller: "mainExploreController",
			controllerAs: "explore"
		})
		.state('neighborhood', {
			url: '/neighborhood',
			templateUrl: 'app/main/explore/neighborhood.template.html',
			controller: "neighborhoodController",
			controllerAs: "neighborhood"
		})
		.state('bills', {
			url: '/bills',
			templateUrl: 'app/main/bills/bills.template.html',
			controller: 'billsController',
			controllerAs: 'bills'
		});
		$urlRouterProvider.otherwise('/intro');
	}

})();
