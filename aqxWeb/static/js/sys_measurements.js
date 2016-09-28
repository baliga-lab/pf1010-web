"use strict";

var app = angular.module('aqx');

app.controller('MeasurementController', function ($scope, $http, $timeout) {
    $scope.message = false;
    $scope.error = false;


    // console.log($scope.boardForm.inputdate.$viewValue);

    $scope.clearMessage = function() {
        $scope.message = false;
        $scope.error = false;
    };

    $scope.addMeasurement = function (measure) {
        measure.system_uid = angular.element('#UID').html();
        measure.min = Number(angular.element('#measure-value').attr('min'));
        measure.max = Number(angular.element('#measure-value').attr('max'));
        // For angular datetime inputs, the value is kept in a different private scope
        // Because of this, ng-bind and ng-model can't reference anything in this scope
        // To get the datetime value, we have to go to the actual DOM element.
        measure.datetime = $scope.boardForm.measureDateTime.$modelValue;
        console.log(measure);
        // Convert datetime's timezone to UTC
        if (measure.datetime) {
            var month = measure.datetime.getMonth() + 1;
            measure.time = measure.datetime.getFullYear() + '-' +
                month + '-' +
                measure.datetime.getDate() + ' ' +
                measure.datetime.toTimeString().split(' ')[0];
            // measure.time = new Date(Date.UTC(measure.datetime.getFullYear(),
            //     measure.datetime.getMonth(),
            //     measure.datetime.getDate(),
            //     measure.datetime.getHours(),
            //     measure.datetime.getMinutes(),
            //     measure.datetime.getSeconds()
            // ));
        }

        function onSuccess(response) {
            console.log(response);
            $scope.error1 = false;
            $scope.error2 = false;
            $scope.message = true;
            $scope.measure.value = "";
            $timeout(function() {
                $scope.message = false;
            }, 3500);
        }
        function onFailure(error) {
            console.log(error);
            console.log(error.data.error);
            if (error.data.error == "Time required") {
                $scope.error1 = false;
                $scope.error2 = true;
                $timeout(function() {
                    $scope.error2 = false;
                }, 3500);
            } else if (error.data.error == "Value required"
                || error.data.error == "Value too high or too low") {
                $scope.error2 = false;
                $scope.error1 = false;
            } else {
                $scope.error2 = false;
                $scope.error1 = true;
                $timeout(function() {
                    $scope.error1 = false;
                }, 3500);
            }
        }

        $http.put('/dav/aqxapi/v1/measurements', measure).then(onSuccess, onFailure);
    }
});