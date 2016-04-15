"use strict";

var app = angular.module('aqx');

app.controller('MeasurementController', function ($scope, $http) {

    $scope.addMeasurement = function (measure) {
        $scope.message = false;

        measure.system_uid = angular.element('#UID').html();

        console.log(measure);

        function onSuccess(response) {
            console.log(response);
            $scope.message = true;
        }
        function onFailure(error) {
            console.log(error);
        }

        $http.put('/dav/aqxapi/v1/measurements', measure).then(onSuccess, onFailure);
    }
});