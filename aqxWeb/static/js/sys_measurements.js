"use strict";

var app = angular.module("aqx");

app.controller('MeasurementController', function ($scope, $http) {
    $scope.addMeasurement = function () {
        function onSuccess(response) {
            console.log(repsonse);
        }
        function onFailure(error) {
            console.log(error);
        }
        var measurement = {
                'system_uid': response.data.systemUID,
                'measurement_id': 'aqxs_' + response.data.measurement_id + '_' + response.data.systemUID,
                'time': response.data.time,
                'value': response.data.value
            }
        console.log(measurement);

        //$http.post('/aqxapi/v1/measurements', measurement).then(onSuccess, onFailure);
    }
});