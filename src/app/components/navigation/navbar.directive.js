(function() {
  'use strict';

  angular
    .module('policynet')
    .directive('uiNavbar', uiNavbar);

  /** @ngInject */
  function uiNavbar() {
    var directive = {
      restrict: 'E',
      templateUrl: 'app/components/navigation/navbar.html',
      // scope: {
          // creationDate: '='
      // },
      controller: NavbarController,
      controllerAs: 'vm',
      bindToController: true
    };

    return directive;

    /** @ngInject */
    function NavbarController($scope, $rootScope) {
    	var vm = this;
    	var sidenavScope = angular.element("md-sidenav").scope();
    	var sections = $rootScope.sections;

    	var deepsearch = function(obj, key, val){
    		if (_.has(obj, key) && obj[key] === val) {return [obj];}
    		return _.flatten(_.map(obj, function(v) {
    			return typeof(v) === "object" ? deepsearch(v, key, val) : [];
    		}), true);
    	};

    	$scope.toggleMenu = function(){
    		sidenavScope.vm.menu_open = !sidenavScope.vm.menu_open;
    	};

    	$rootScope.$watch('$state.current.url', function(newVal){
    		var pageObj = deepsearch(sections, "url", newVal);
    		vm.stateName = pageObj.length === 1 ? pageObj[0].name : "";
    		vm.subheading = pageObj.length === 1 ? pageObj[0].subheading : "";
    	});

    }
  }

})();
