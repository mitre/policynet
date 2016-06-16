(function() {
  'use strict';

  angular
    .module('policynet')
    .config(config);

  /** @ngInject */
  function config($logProvider, $compileProvider, $mdThemingProvider, toastr) {
    // Enable log
    $logProvider.debugEnabled(true);

    // Set options third-party lib
    toastr.options.timeOut = 3000;
    toastr.options.positionClass = 'toast-top-right';
    toastr.options.preventDuplicates = true;
    toastr.options.progressBar = true;

    $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|chrome-extension|data):/);

		$mdThemingProvider.theme('default')
			.primaryPalette('blue')
			.accentPalette('green');

		$mdThemingProvider.definePalette('neutral', {
			'50': 'rgba(256,256,256,1)',
			'100': "rgb(31,119,180)",
			'200': "rgb(255,127,14)",
			'300': "rgb(127,127,127)",
			'400': "rgb(214,39,40)",
			'500': "rgb(44,160,44)",
			'600': "rgb(140,86,75)",
			'700': "rgb(227,119,194)",
			'800': "rgb(148,103,189)",
			'900': "rgb(188,189,34)",
			'A100': "rgb(23,190,207)",
			'A200': 'ff5252',
			'A400': 'ff1744',
			'A700': 'd50000',
			'contrastDefaultColor': 'light',    // whether, by default, text (contrast)
			                                  // on this palette should be dark or light
			'contrastDarkColors': ['50', '100', // hues which contrast should be 'dark' by default
			'200', '300', '400', 'A100'],
			'contrastLightColors': undefined    // could also specify this if default was 'dark'
		});
		$mdThemingProvider.theme('inline-toolbar')
			.primaryPalette('neutral', {
				"default": "50",
				"hue-1": "100",
				"hue-2": "200",
				"hue-3": "500"
			})
			.accentPalette('blue')//;
			.backgroundPalette('neutral');
  }

})();
