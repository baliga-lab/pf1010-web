/**
 * Created by Brian on 2/14/2016.
 */
$(document).ready(function() {

    function buildContentString(dataPoint) {
        return "<h2>" + dataPoint.title + "</h2>" +
            "<ul><li>Aquaponics Technique: " + dataPoint.description['aqx_techniques'] + "</li>" +
            "<li>Aquatic organism: " + dataPoint.description['aqx_organism'] + "</li>" +
            "<li>Growbed Medium: " + dataPoint.description['growbed_media'] + "</li>" +
            "<li>Crop: " + dataPoint.description['crop'] + "</li></ul>";
    }

    function addMarker(dataPoint) {
        var latLng = new google.maps.LatLng(dataPoint.lat, dataPoint.lng);
        var content = buildContentString(dataPoint);
        marker1 = new google.maps.Marker({
            title: dataPoint.title,
            position: latLng,
            map: map,
            content: content
        });

        google.maps.event.addListener(marker1, 'mouseover', (function (marker1, content) {
            return function () {
                infoWindow.setContent(content);
                infoWindow.open(map, marker1);
            }
        })(marker1, content));

        google.maps.event.addListener(marker1, 'mouseout', (function () {
            return function () {
                infoWindow.close();
            }
        })(marker1));
    }

    function initializeMap() {
        var myLatLng = {lat: 57.9, lng: 14.6};

        map = new google.maps.Map(document.getElementById('map'), {
            zoom: 4,
            center: myLatLng
        });

        infoWindow = new google.maps.InfoWindow({
            maxWidth: 250
        });
        for (var i = 0, length = json_ob.length; i < length; i++) {
            var data = json_ob[i];{
                addMarker(data);
            }
        }
    }
    initializeMap();
});
//$(document).ready(function(){
//    $('#map').html("jQuery is working");
//});
