"use strict"

var app = angular.module('aqx');

app.controller('AddEmailController', function ($scope, $http) {
    $scope.addEmail = function(email) {
        console.log(email);
        function onSuccess(response) {
            console.log(response);
        }

        function onFailure(error) {
            console.log(error);
        }
        $http.post('/aqx/v1/mailing', email).then(onSuccess, onFailure);
    };
});