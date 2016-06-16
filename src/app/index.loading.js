(function() {
  'use strict';

  angular
    .module('policynet')
    .run(loading);

  /** @ngInject */
  function loading($rootScope){
	$rootScope.showload = false;
	$rootScope.$on('loading', function(e,tf){
		$rootScope.showload = tf;
	});
  }

})();
