(function(angular, jQuery, undefined) {
    if (!String.prototype.format) {
	String.prototype.format = function () {
	    var i = 0, args = arguments;
	    return this.replace(/{}/g, function () {
		return typeof args[i] != 'undefined' ? args[i++] : '';
	    });
	};
    }

    jQuery(document).ready(function() {
	jQuery.material.init();
    });

    angular.module('moolah', ['ngRoute', 'ngResource', 'ngMaterial', 'ngMessages', 'chart.js', 'cgBusy'])

	.config(['$httpProvider', '$routeProvider', '$resourceProvider', 'STATIC_URL',
		 function($httpProvider, $routeProvider, $resourceProvider, STATIC_URL) {

		     var toStatic = function(i) {
			 return '{}{}'.format(STATIC_URL, i);
		     };

		     $httpProvider.defaults.xsrfCookieName = 'csrftoken';
		     $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
		     $resourceProvider.defaults.stripTrailingSlashes = false;

		     $routeProvider
			 .when('/', {
			     templateUrl: toStatic('views/dashboard.html'),
			     controller: 'DashboardController',
			     controllerAs: 'dashboardCtrl'
			 })
			 .when('/reports', {
			     templateUrl: toStatic('views/reports.html'),
			     controller: 'ReportsController',
			     controllerAs: 'reportCtrl'
			 })
			 .when('/export', {
			     templateUrl: toStatic('views/export.html'),
			     controller: 'ExportController',
			     controllerAs: 'exportCtrl'
			 });
		 }])

	.factory('toStatic', ['STATIC_URL', function(STATIC_URL) {
	    return function(i) {
		return '{}{}'.format(STATIC_URL, i);
	    };
	}])

	.factory('Transaction', ['$resource', 'API_URL', function($resource, API_URL) {
	    return $resource('{}transactions/:id'.format(API_URL));
	}])

	.factory('Purchase', ['$resource', 'API_URL', function($resource, API_URL) {
	    return $resource('{}purchases/:id'.format(API_URL));
	}])

	.factory('Category', ['$resource', 'API_URL', function($resource, API_URL) {
	    return $resource('{}categories/:id'.format(API_URL));
	}])

	.factory('PurchaseBalance', ['$http', 'API_URL', function($http, API_URL) {
	    return function() {
		return $http.get('{}purchases/total/'.format(API_URL));
	    };
	}])

	.factory('SummaryReport', ['$http', 'API_URL', function($http, API_URL) {
	    return function() {
		return $http.get('{}reports/summary/'.format(API_URL));
	    };
	}])

	.factory('RateBreakdownReport', ['$http', 'API_URL', function($http, API_URL) {
	    return function() {
		return $http.get('{}reports/rates/'.format(API_URL));
	    };
	}])

	.factory('YearlyReport', ['$http', 'API_URL', function($http, API_URL) {
	    return function() {
		return $http.get('{}reports/savings/'.format(API_URL));
	    };
	}])

	.factory('WeeklyReport', ['$http', 'API_URL', function($http, API_URL) {
	    return function() {
		return $http.get('{}reports/week/'.format(API_URL));
	    };
	}])

	.factory('AllowanceReport', ['$http', 'API_URL', function($http, API_URL) {
	    return function() {
		return $http.get('{}reports/allowance/'.format(API_URL));
	    };
	}])

	.factory('StatsReport', ['$http', 'API_URL', function($http, API_URL) {
	    return function() {
		return $http.get('{}reports/stats/'.format(API_URL));
	    };
	}])

	.controller('moolahNavController', ['$location', 'LOGOUT_URL', 'USER_NAME', function($location, LOGOUT_URL, USER_NAME) {
	    var self = this;

	    self.logoutUrl = LOGOUT_URL;
	    self.userName = USER_NAME || 'Account';

	    self.isActive = function(path) {
		return $location.path() === path;
	    };

	}]).directive('moolahNav', ['toStatic', function(toStatic) {
	    return {
		restrict: 'E',
		controller: 'moolahNavController',
		controllerAs: 'navController',
		templateUrl: toStatic('views/nav.html')
	    };
	}])

	.directive('ratePieChart', ['toStatic', function(toStatic) {
	    return {
		restrict: 'E',
		controller: 'RatePieChartController',
		controllerAs: 'pieChartCtrl',
		templateUrl: toStatic('views/rate-pie-chart.html'),
		bindToController: true,
		scope: {}
	    };
	}]).controller('RatePieChartController', ['RateBreakdownReport', function(RateBreakdownReport) {
	    var self = this;

	    RateBreakdownReport().success(function(d) {
		self.income = d.income;
		self.expense = d.expense;
		self.total = d.total;
	    });

	}])

	.directive('yearlySavingsGraph', ['toStatic', function(toStatic) {
	    return {
		restrict: 'E',
		controller: 'YearlySavingsGraphController',
		controllerAs: 'reportCtrl',
		templateUrl: toStatic('views/yearly-savings-graph.html'),
		bindToController: true,
		scope: {}
	    };
	}]).controller('YearlySavingsGraphController', ['YearlyReport', function(YearlyReport) {
	    var self = this;

	    self.options = {
		pointDot : false,
		pointHitDetectionRadius: 0,
		scaleShowVerticalLines: false,
		scaleFontSize: 0,
		tooltipTemplate: function(obj) {
		    var label = '{} days ago'.format(obj.label),
			value;

		    if (obj.value < 0) {
			value = '-${}'.format(obj.value);
		    } else {
			value = '${}'.format(obj.value);
		    }

		    return '{} : {}'.format(label, value);
		}
	    };

	    YearlyReport().success(function(d) {
		self.data = d.data;
		self.labels = d.labels;
		self.serieis = d.series;
	    });

	}])

	.directive('weeklyGraph', ['toStatic', function(toStatic) {
	    return {
		restrict: 'E',
		controller: 'WeeklyGraphController',
		controllerAs: 'reportCtrl',
		templateUrl: toStatic('views/weekly-graph.html'),
		bindToController: true,
		scope: {}
	    };
	}]).controller('WeeklyGraphController', ['WeeklyReport', function(WeeklyReport) {
	    var self = this;

	    self.cardTitle = 'This Week';

	    WeeklyReport().success(function(d) {
		self.data = d.data;
		self.labels = d.labels;
		self.series = d.series;
	    });
	}])

	.directive('allowanceBalances', ['toStatic', function(toStatic) {
	    return {
		restrict: 'E',
		controller: 'AllowanceBalancesController',
		controllerAs: 'reportCtrl',
		templateUrl: toStatic('views/allowance-balances.html'),
		bindToController: true,
		scope: {}
	    };
	}]).controller('AllowanceBalancesController', ['AllowanceReport', function(AllowanceReport) {
	    var self = this;

	    self.reportPromise = AllowanceReport();

	    self.reportPromise.success(function(d) {
		self.data = d;
	    });
	}])

	.directive('randomStats', ['toStatic', function(toStatic) {
	    return {
		restrict: 'E',
		controller: 'RandomStatsController',
		controllerAs: 'reportCtrl',
		templateUrl: toStatic('views/random-stats.html'),
		bindToController: true,
		scope: {}
	    };
	}]).controller('RandomStatsController', ['StatsReport', function(StatsReport) {
	    var self = this;

	    self.reportPromise = StatsReport();

	    self.reportPromise.success(function(d) {
		self.data = d;
	    });
	}])

	.controller('DashboardController', ['Purchase', 'PurchaseBalance', 'Transaction', 'SummaryReport', 'Category', 
		function(Purchase, PurchaseBalance, Transaction, SummaryReport, Category) {

	    var self = this;

		self.getAllCategories = function() {
			self.categoriesPromise = Category.query().$promise;
			self.categoriesPromise.then(function(data) {
				self.allCategories = data;
			})
		};

		self.readOnly = false;
		self.filterSelected = true;
		var cachedQuery;
		self.getAllCategories();
		self.categories = [];
		self.querySearch = querySearch;

		function querySearch (query) {
			cachedQuery = cachedQuery || query;
			var result = self.allCategories.filter(createFilterFor(query));
			// var result = cachedQuery ? self.allCategories.filter(createFilterFor(cachedQuery)) : [];
			return result;
		}

		function createFilterFor(query) {
			var lowercaseQuery = angular.lowercase(query);
			return function filterFn(cat) {
				return (angular.lowercase(cat.name).indexOf(lowercaseQuery) != -1);
			};
		}

	    self.reloadTransactions = function() {
			self.transactionPromise = Transaction.query().$promise;
			self.transactionPromise.then(function(d) {
				self.todaysTransactions = d;
				var values = d.map(function(i) { return i.amount; });
				self.todaysTransactionsTotal = values.reduce(function(a, b) {
				return Number(a) + Number(b);
				}, 0);

				self.totalIsPositive = self.todaysTransactionsTotal > 0;
			});
	    };

	    self.reloadPurchases = function() {
			self.allowancePromise = Purchase.query().$promise;
			self.allowancePromise.then(function(d) {
				self.purchases = d;
			});
			PurchaseBalance().then(function(d) {
				self.purchaseBalance = d.data.balance;
				self.balanceIsPositive = self.purchaseBalance > 0;
			});
	    };

	    self.reloadSummary = function() {
		self.summaryPromise = SummaryReport();
		self.summaryPromise.then(function(d) {
		    self.summary = d.data;
		});
	    };

	    self.submitTransaction = function() {
		var svc;

		if (self.newTransaction.allowance) {
		    svc = Purchase;
		} else {
		    svc = Transaction;
		}

		svc.save(self.newTransaction, function() {
		    if (self.newTransaction.allowance) {
			self.reloadPurchases();
		    } else {
			self.reloadTransactions();
			self.reloadSummary();
		    }
		    self.newTransaction = {};
		});
	    };

	    self.reloadTransactions();
	    self.reloadSummary();
	    self.reloadPurchases();

	}])

	.controller('ReportsController', [function() {
	    var self = this;
	}])

	.controller('ExportController', ['$http', 'API_URL', function($http, API_URL) {
	    var self = this;

	    var defaultFilters = function() {
		self.filters = {
		    transactionType: 'b'
		};
	    };

	    defaultFilters();

	    self.goGoGadgetExport = function() {
		$http
		    .post('{}reports/export/'.format(API_URL), self.filters)
		    .success(function(data, status, headers, config) {
			var anchor = angular.element('<a/>');
			anchor.attr({
			    href: 'data:attachment/csv;charset=utf-8,' + encodeURI(data),
			    target: '_blank',
			    download: 'export.csv'
			})[0].click();

		    });
	    };
	}]);

}(angular, jQuery));
