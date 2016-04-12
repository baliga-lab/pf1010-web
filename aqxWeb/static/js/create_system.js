"use strict";

var app = angular.module('aqx');

app.controller('CreateSystemController', function ($scope, $http) {

    $scope.system = {
        location: {
            lat: null,
            lng: null
        },
        gbMedia: [{}],
        crops: [{}],
        organisms: [{}]
    };

    $scope.create = function(system) {
        function onSuccess(response) {
            console.log(response);
        }
        function onFailure(error) {
            console.error(error);
        }
        $http.post('/aqxapi/v2/system', system).then(onSuccess, onFailure);
    }

    $scope.geocode = function(address) {
        var geocoder = new google.maps.Geocoder();
        geocoder.geocode({ 'address': address }, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                $scope.system.location.lat = results[0].geometry.location.lat();
                $scope.system.location.lng = results[0].geometry.location.lng();
            }
            else {
                alert("Geocode was not successful for the following reason: " + status);
            }
        });
    }
});