(function() {
	'use strict';

	angular
	.module('policynet')
	.directive('uiSidebar', uiSidebar);

	/** @ngInject */
	function uiSidebar() {
		var directive = {
			templateUrl: 'app/components/navigation/sidebar-menu.html',
			scope: {

			},
			controller: SidebarController,
			controllerAs: 'vm',
			bindToController: true
		};

		return directive;

		/** @ngInject */
		function SidebarController($scope, $rootScope) {
			var vm = this;
			this.state = $rootScope.$state;
			vm.menu_open = true;
			vm.sections = $rootScope.sections;
		}
	}

})();
