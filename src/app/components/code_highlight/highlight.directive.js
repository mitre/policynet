/*globals Prism */
(function() {
  'use strict';

  angular
    .module('policynet')
    .directive('uiHighlighter', uiHighlighter);

  /** @ngInject */
  function uiHighlighter($interpolate) {
    var directive = {
		restrict: 'E',
		templateUrl: 'app/components/code_highlight/highlight.template.html',
		replace: true,
		transclude: true,
		link: function (scope, elm) {
			var tmp = $interpolate(elm.find('code').text())(scope);
			elm.find('code').html(Prism.highlight(tmp, Prism.languages.xml));
		}
	};
    return directive;
  }

})();
