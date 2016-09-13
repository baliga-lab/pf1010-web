'use strict';

var app = angular.module('aqx');

app.controller('EditDataController', function ($scope, $filter, $http, $timeout) {

    $scope.measurementName = angular.element('#measurementName').html();
    var created_at = angular.element('#createdAt').html();

    $scope.message = false;
    $scope.error1 = false;
    $scope.error2 = false;

    $scope.measure = {'time': created_at};

    $scope.editMeasurement = function (measure) {

        $scope.message = false;
        $scope.error1 = false;
        $scope.error2 = false;

        measure.system_uid = angular.element('#UID').html();
        measure.min = Number(angular.element('#measure-value').attr('min'));
        measure.max = Number(angular.element('#measure-value').attr('max'));
        measure.measurement_name = $scope.measurementName;
        var newDate = new Date();
        var month = newDate.getMonth() + 1;
        measure.updated_at = newDate.getFullYear() + '-' +
            month + '-' +
            newDate.getDate() + ' ' +
            newDate.toTimeString().split(' ')[0];

        console.log(measure);

        function onSuccess(response) {
            console.log(response);
            $scope.error1 = false;
            $scope.message = true;
            $timeout(function() {
                $scope.message = false;
            }, 3500);
        }
        function onFailure(error) {
            console.log(error);
            console.log(error.data.error);
            if (error.status == 400){
                $scope.error1 = true;
                $scope.error2 = false;
                $timeout(function() {
                    $scope.error1 = false;
                }, 3500);
            }else {
                $scope.error1 = false;
                $scope.error2 = true;
                $timeout(function() {
                    $scope.error2 = false;
                }, 3500);
            }


        }
        $http.put('/dav/aqxapi/v1/measurements/update', measure).then(onSuccess, onFailure);
    }
});
