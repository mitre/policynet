(function() {
  'use strict';

  angular
    .module('policynet')
    .run(runBlock);

  /** @ngInject */
  function runBlock($log) {

    $log.debug('runBlock end');
  }

})();
