/*globals _ */
/*jslint browser: true*/
(function() {
	'use strict';

	angular
	.module('policynet')
	.controller('billsController', billsController);

	/** @ngInject */
	function billsController($scope, $mdDialog, query) {
		$scope.page = "bills";
		$scope._ = _;

		$scope.query_string = "";
		$scope.table_query = {
			qs: "",
			order: 'score',
			limit: 0,
			page: 0,
			total: 0,
			itemPerPage: [20]
		};


		$scope.search = function(){
			$scope.table_query.qs = $scope.query_string;
			$scope.bill_search().then(function(data){
				$scope.bills_data = data;
				$scope.table_query.limit = data.page.count;
				$scope.table_query.total = data.count;
				$scope.table_query.page = data.page.page;
				$scope.itemPerPage = data.page.per_page;
			});
		};


		$scope.bill_search = function(page, limit, order){
			$scope.close_bill_text();
			page = page || 1;
			limit = limit || 20;
			order = order || "score";
			if (order[0] === "-"){
				order = order.substr(1) + "__asc";
			}


			return query.get("bill_search", {
				query: $scope.table_query.qs,
				page: page,
				limit: limit,
				order: order
			}, true).then(function(data){

				data.results.forEach(function(bill){
					bill.last_version.formats = _.keys(bill.last_version.urls);
				});

				$scope.$emit('loading', false);
				return data;
			});
		};

		// $scope.get_redline = function(bill_id){
		// 	$scope.text = {};
		// 	query.get("bill_get", {
		// 		bill_id: bill_id,
		// 		action: "redline"
		// 	}, true).then(function(data){
		// 		$scope.text.redline = data;
		// 		$scope.$emit('loading', false);
		// 	});
		// };

		$scope.format_bill_xml = function(ev, bill_id){
			var confirm = $mdDialog.confirm()
				.title('Show formatted XML?')
				.textContent('Display formatted XML might take a few seconds, depending on how large the bill is.')
				.targetEvent(ev)
				.ok('Format away!')
				.cancel('Never mind. I don\'t have time.');
			$mdDialog.show(confirm).then(function() {
				$scope.get_bill_text(bill_id, 'xml');
			});
		};

		$scope.get_bill_text = function(bill_id, action){
			$scope.text = {};
			query.get("bill_get", {
				bill_id: bill_id,
				action: action
			}, true).then(function(data){
				$scope.text[action] = data;

				$scope.$emit('loading', false);
			});
		};

		$scope.close_bill_text = function(){
			delete $scope.text;
		};

		$scope.get_text = function(url, format){
			query.get("get_text", {
				url: url,
				format: format
			}, true).then(function(data){
				$scope.$emit('loading', false);
				$scope.show_text(data);
			});
		};

		$scope.show_text = function(bill_text){
			$mdDialog.show({
				controller: ChangeTextController,
				templateUrl: 'app/main/bills/changeText.template.html',
				parent: angular.element(document.body),
				// targetEvent: ev,
				clickOutsideToClose: true,
				locals: {
					bill_text: bill_text
				},
				bindToController: true
			});
		};

		/** @ngInject */
		function ChangeTextController($scope, $mdDialog, bill_text){
			$scope.text = {};
			if (bill_text[0] === "<"){
				$scope.text.xml = bill_text;
			} else {
				$scope.text.text = bill_text;
			}
			$scope.cancel = function(){
				$mdDialog.cancel();
			};
		}

		$scope.onChangeOrder = function(order){
			$scope.bill_search($scope.table_query.page, $scope.table_query.limit, order).then(function(data){
				$scope.bills_data = data;
				$scope.table_query.limit = data.page.count;
				$scope.table_query.total = data.count;
				$scope.table_query.page = data.page.page;
				$scope.itemPerPage = data.page.per_page;
			});
		};

		$scope.onPaginationChange = function(page, limit){
			//TODO
			page = page;
			limit = limit;
		};
	}
})();
