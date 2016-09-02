var app = angular.module('aqx', ['angularUtils.directives.dirPagination']);


// Flask's Jinja2 template engine takes precedence over angular's expressions
// Angular and Jinja2 both use {{ }} for expressions, so we can actually convert the "interpolator"
// symbol from:
// {{ -> {a
// and
// }} -> a}
// Now variables in an Angular controller's scope can be referenced in HTML using {a a}
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);

