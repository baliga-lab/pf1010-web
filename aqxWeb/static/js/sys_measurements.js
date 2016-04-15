"use strict";

var app = angular.module('aqx');

app.controller('MeasurementController', function ($scope, $http) {

    $scope.addMeasurement = function (measure) {
        $scope.message = false;

        function onSuccess(response) {
            console.log(response);
            $scope.message = true;
        }
        function onFailure(error) {
            console.log(error);
        }
        console.log(measure);

        $http.post('dav/aqxapi/v1/measurements', measure).then(onSuccess, onFailure);
    }
});