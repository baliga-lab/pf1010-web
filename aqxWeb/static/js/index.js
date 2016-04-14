"use strict";

var app = angular.module('aqx');

app.controller('AddEmailController', function ($scope, $http) {
    $scope.message = false;

    $scope.addEmail = function(email) {
        function onSuccess(response) {
            console.log(response);
            $scope.message = true;
        }
        function onFailure(error) {
            console.log(error);
        }
        $http.post('/aqxapi/v2/mailing', {email: email}).then(onSuccess, onFailure);
    };
});