/*jslint browser: true*/
(function() {
	'use strict';

	angular
		.module('policynet')
		.factory('query', query);

	/** @ngInject */
	function query($log, $http, toastr, $rootScope, $q) {
		var apiURL = window.location.protocol + "//" + window.location.hostname + ":" + window.location.port + "/api/";

		function get_http(url, emit){
			if (emit){
				$rootScope.$emit('loading',true);
			}
			return $http.get(url)
					 	.then(querySuccess, queryError);
		}

		function get(query, params, emit){
			if (emit){
				$rootScope.$emit('loading',true);
			}
			var url = apiURL + query;

			return $http.get(url, {params: params})
					 	.then(querySuccess, queryError);
		}
		function querySuccess(res){
			if (res.data.status === "failed"){
				$log.error('Query failed: ' + angular.toJson(res.data, true));
				toastr.error('Query failed: ' + res.data.message);
				return $q.reject(new Error(res.data.message));
			} else {
				return res.data;
			}

		}

		function queryError(res){
			$log.error('XHR failed: ' + angular.toJson(res.data, true));
			toastr.error('XHR failed: ' + res.data);
		}

		return {
			get: get,
			get_http: get_http
		};
	}
})();
