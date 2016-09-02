'use strict';

var app = angular.module('aqx');

(app.controller('viewDataController', function ($scope, $filter, $http) {


    var system_uid = angular.element('#UID').html();
    var measurementName = angular.element('#meaurementName').html();

    var getDataForPage = function(page){
        $http.get('/dav/aqxapi/measurements/' + measurementName + '/system/' + system_uid + '/' + page)
            .success(function(data){
                $scope.measurements = data;
                $scope.items = data['data'];
                $scope.totalPages = data['total_pages'];
            });
    };

    var init = function(){
        getDataForPage(1);
        $scope.itemsPerPage = 20;
        $scope.gap = 5;
        $scope.currentPage = 1;
    };

    $scope.range = function (size, start, end) {
        var ret = [];
        if (size < end) {
            end = size;
            start = Math.max(size-$scope.gap, 1);
        }
        for (var i = start; i <= end; i++) {
            ret.push(i);
        }
        return ret;
    };

    $scope.prevPage = function () {
        if ($scope.currentPage > 1) {
            $scope.currentPage--;
            getDataForPage($scope.currentPage);
        }
    };

    $scope.nextPage = function () {
        if ($scope.currentPage < $scope.totalPages) {
            $scope.currentPage++;
            getDataForPage($scope.currentPage);
        }
    };

    $scope.setPage = function () {
        $scope.currentPage = this.n;
        getDataForPage($scope.currentPage);
    };

    init();
}));