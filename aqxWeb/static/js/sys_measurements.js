"use strict";

var app = angular.module('aqx');

app.controller('MeasurementController', function ($scope, $http, $timeout) {
    $scope.message = false;
    $scope.error = false;

    $scope.min = document.getElementById("measure-value").min;
    $scope.max = document.getElementById("measure-value").max;

    $scope.clearMessage = function() {
        $scope.message = false;
        $scope.error = false;
    };

    $scope.addMeasurement = function (measure) {
        measure.system_uid = angular.element('#UID').html();
        measure.min = Number(angular.element('#measure-value').attr('min'));
        measure.max = Number(angular.element('#measure-value').attr('max'));

        // Convert datetime's timezone to UTC
        if (measure.time) {
            measure.time = new Date(Date.UTC(measure.time.getFullYear(),
                measure.time.getMonth(),
                measure.time.getDate(),
                measure.time.getHours(),
                measure.time.getMinutes(),
                measure.time.getSeconds()
            ));
        }

        console.log(measure);

        function onSuccess(response) {
            console.log(response);
            $scope.message = true;
            $scope.error = false;
            $scope.measure.time = "";
            $scope.measure.value = "";
            $timeout(function() {
                $scope.message = false;
            }, 3500);
        }
        function onFailure(error) {
            console.log(error.data.error);
            if (error.data.error == "Time required" || error.data.error == "Value required"
                    || error.data.error == "Value too high or too low") {
                $scope.error = false;
            } else {
                $scope.error = true;
                $timeout(function() {
                    $scope.error = false;
                }, 3500);
            }
        }

        $http.put('/dav/aqxapi/v1/measurements', measure).then(onSuccess, onFailure);
    }
});