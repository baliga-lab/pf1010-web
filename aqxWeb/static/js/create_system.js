"use strict";

var app = angular.module('aqx');

app.controller('CreateSystemController', function ($scope, $http, $window) {
    $scope.error = false;

    $scope.system = {
        location: {},
        gbMedia: [{}],
        crops: [{}],
        organisms: [{}]
    };

    $scope.create = function(system) {
        system.gbMedia[0].count = 1;

        // Convert datetime's timezone to UTC
        if (system.startDate) {
            system.startDate = new Date(Date.UTC(system.startDate.getFullYear(),
                system.startDate.getMonth(),
                system.startDate.getDate(),
                0, 0, 0));
        }

        console.log(system);

        function onSuccess(response) {
            console.log(response);
            var socSystem = {
                'user': response.data.userID,
                'system': {
                    'system_id': response.data.systemID,
                    'system_uid': response.data.systemUID,
                    'name': system.name,
                    'description': system.name,
                    'location_lat': system.location.lat,
                    'location_lng': system.location.lng,
                    'status': 100
                }
            };
            $http.post('/social/aqxapi/v1/system', socSystem).then(onSuccess2, onFailure);
            $window.location.href = '/system/' + response.data.systemUID + '/measurements';
        }
        function onSuccess2(response) {
            console.log(response);
        }
        function onFailure(error) {
            console.error(error);
            $scope.error = true;
        }
        $http.post('/aqxapi/v2/system', system).then(onSuccess, onFailure);
    };

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
    };
});