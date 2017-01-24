"use strict";

/*
 * This is the replacement of the Angular 1 based measurment form, which is
 */
var aqx_measurements;
if (!aqx_measurements) {
    aqx_measurements = {};
}

(function () {
    function toIntString2(i) {
        return i < 10 ? '0' + i.toString() : i.toString();
    }

    function getTimeStringUTC(time) {
        return toIntString2(time.getUTCHours()) + ':' + toIntString2(time.getUTCMinutes()) +
            ':' + toIntString2(time.getUTCSeconds());
    }
    aqx_measurements.makeDateTimeString = function(date, time) {
        return date.getFullYear() + '-' +
            (date.getMonth() + 1) + '-' +
            date.getDate() + ' ' +
            getTimeStringUTC(time);
    };
    aqx_measurements.timeStringToDate = function (timeStr) {
        var parts = timeStr.split(' ');
        var result;
        if (parts.length > 0) {
            var timeParts = parts[0].split(':');
            var hours = parseInt(timeParts[0]);
            var minutes = parseInt(timeParts[1]) % 60;
            if (parts.length >= 2) {
                if (parts[1] == 'AM' && hours == 12) hours = 0;
                else if (parts[1] == 'PM' && hours < 12) hours += 12;
            }
            result = new Date(Date.UTC(1900, 0, 1, hours, minutes));
        }
        return result;
    };
}());


// This is the old Angular based stuff. TODO: Replace
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
        measure.min = Number(angular.element('#measure-value').attr('min'));
        measure.max = Number(angular.element('#measure-value').attr('max'));
        // For angular datetime inputs, the value is kept in a different private scope
        // Because of this, ng-bind and ng-model can't reference anything in this scope
        // To get the datetime value, we have to go to the actual DOM element.
        //var measureDate = $scope.boardForm.measureDate.$modelValue;
        //var measureTime = $scope.boardForm.measureTime.$modelValue;
        var measureDate = new Date($('#measure-date').val());
        var measureTime = aqx_measurements.timeStringToDate($('#measure-time').val());
        console.log(measureDate);
        console.log(measureTime);
        measure.time = aqx_measurements.makeDateTimeString(measureDate, measureTime);
        console.log(measure);

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
