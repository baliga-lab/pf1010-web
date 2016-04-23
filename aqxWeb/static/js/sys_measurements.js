"use strict";

var app = angular.module('aqx');

app.controller('MeasurementController', function ($scope, $http, $timeout) {
    $scope.message = false;
    $scope.error = false;

    $scope.clearMessage = function() {
        $scope.message = false;
        $scope.error = false;
    };

    $scope.addMeasurement = function (measure) {
        measure.system_uid = angular.element('#UID').html();

        console.log(measure);

        function onSuccess(response) {
            console.log(response);
            $scope.message = true;
            $scope.error = false;
            $scope.measure.time = "";
            $scope.measure.value = "";
            $timeout(function() {
                $scope.error = false;
            }, 3500);
        }
        function onFailure(error) {
            console.log(error);
            $scope.error = true;
            $timeout(function() {
                $scope.error = false;
            }, 7500);
        }

        $http.put('/dav/aqxapi/v1/measurements', measure).then(onSuccess, onFailure);
    }
});