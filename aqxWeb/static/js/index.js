"use strict";

var app = angular.module('aqx');

app.controller('AddEmailController', function ($scope, $http) {

    $scope.addEmail = function(email) {
        function onSuccess(response) {
            console.log(response);
        }
        function onFailure(error) {
            console.log(error);
        }
        $http.post('/aqxapi/v1/mailing', {email: email}).then(onSuccess, onFailure);
    };
});