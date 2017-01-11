"use strict";

var aqx_social;
if (!aqx_social) {
    aqx_social = {};
}

(function () {
    aqx_social.getUserConsent = function() {
        return confirm('Are you sure?');
    }

    aqx_social.renderGoogleMaps = function(latitude, longitude, systemName) {
        var systemLocation = new google.maps.LatLng(latitude, longitude);
        var mapDiv = document.getElementById('map');
        var infowindow = new google.maps.InfoWindow();
        var mapOptions = {
            center: systemLocation,
            zoom: 11,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        }
        var gMap = new google.maps.Map(mapDiv, mapOptions);
        // System Location Marker
        var systemLocationMarker = new google.maps.Marker({
            position: systemLocation,
            map: gMap,
            // Using the global variable which holds the boarding place name
            title: systemName,
            animation: google.maps.Animation.DROP,
            icon: 'https://maps.gstatic.com/mapfiles/ms2/micons/rangerstation.png'
        });
        google.maps.event.addListener(systemLocationMarker, 'mouseover', function () {
            infowindow.setContent(this.title);
            infowindow.open(gMap, this);
        });
    }

}());
