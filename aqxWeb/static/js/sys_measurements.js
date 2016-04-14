"use strict";

var app = angular.module("aqx");

app.controller('MeasurementController', function ($scope, $http) {

    $scope.addMeasurement = function (measure) {
        function onSuccess(response) {
            console.log(repsonse);
        }
        function onFailure(error) {
            console.log(error);
        }
        var measurement = {
                'system_uid': response.data.systemUID,
                'measurement_id': response.data.measurement_id,
                'time': response.data.time,
                'value': response.data.value
            };
        console.log(measure);

        $http.post('/aqxapi/v1/measurements', measurement).then(onSuccess, onFailure);
    }
});