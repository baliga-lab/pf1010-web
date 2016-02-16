/**
 * Created by Brian on 2/14/2016.
 */

/**
 * Created by Brian on 2/14/2016.
 */

//$(document).ready(function () {
//    console.log('document ready');
//    function initializeMap() {
//        console.log('initialize');
//        var myLatLng = {lat: 57.9, lng: 14.6};
//        var myOptions = {
//            center: new google.maps.LatLng(57.9, 14.6),
//            zoom: 4,
//            mapTypeId: google.maps.MapTypeId.ROADMAP
//        };
//        var map = new google.maps.Map(document.getElementById("map"),
//            myOptions);
//    }
//    initializeMap();
//});

$(document).ready(function() {

    var map;

    ////Sample data
    //function uploadClicked() {
    //    //var systemInfo = json_ob;
    //    var filteredSystems = [];
    //
    //    var dropDownObject1 = document.getElementById("selectTechnique");
    //    var dropDownObject2 = document.getElementById("selectOrganism");
    //    var dropDownObject3 = document.getElementById("selectCrop");
    //    var dropDownObject4 = document.getElementById("selectGrowbedMedium");
    //    var dp1 = dropDownObject1.value;
    //    var dp2 = dropDownObject2.value;
    //    var dp3 = dropDownObject3.value;
    //    var dp4 = dropDownObject4.value;
    //    console.log(dp1);
    //    console.log(dp2);
    //    console.log(dp3);
    //    console.log(dp4);
    //
    //    if (dp1 != "Choose an Aquaponics Technique") {
    //        filteredSystems = _.filter(json_ob, function (system) {
    //            return (system.description.aqx_techniques === dp1);
    //        });
    //    } else {
    //        filteredSystems = json_ob;
    //    }
    //
    //    if (dp2 != "Choose an Aquatic Organism") {
    //        filteredSystems = _.filter(filteredSystems, function (system) {
    //            return (system.description.aqx_organism === dp2);
    //        });
    //    }
    //
    //    if (dp3 != "Choose a Crop") {
    //        filteredSystems = _.filter(filteredSystems, function (system) {
    //            return (system.description.crop === dp3);
    //        });
    //    }
    //
    //    if (dp4 != "Choose a Growbed Medium") {
    //        filteredSystems = _.filter(filteredSystems, function (system) {
    //            return (system.description.growbed_media === dp4);
    //        });
    //    }
    //
    //    function removeFilteredMarkers(filteredSystems){
    //        for (var i = 0; i < markers.length; i++) {
    //            for (var j = 0; j < filteredSystems.length; j++){
    //                if (markers[i].title === filteredSystems[j].title){
    //                    markers[i].setMap(null);
    //                }
    //            }
    //        }
    //    }
    //    removeFilteredMarkers(filteredSystems);
    //};
    //
    function populateDropdown(key, elementId){
        var select = document.getElementById(elementId);
        for(var i = 0; i < meta_data[key].length; i++) {
            var opt = meta_data[key][i];
            var el = document.createElement("option");
            el.textContent = opt;
            el.value = opt;
            select.appendChild(el);
        }
    };
    populateDropdown("aqx_techniques", "selectTechnique");
    populateDropdown("aqx_organisms", "selectOrganism");
    populateDropdown("growbed_media", "selectGrowbedMedium");
    populateDropdown("crops", "selectCrop");

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
        markers.push(marker1);
    }

    function setMapOnAll(map) {
        for (var i = 0; i < markers.length; i++) {
            markers[i].setMap(map);
        }
    }
    //
    //function removeFilteredMarkers(filteredSystems){
    //    for (var i = 0; i < markers.length; i++) {
    //        for (var j = 0; j < filteredSystems.length; j++){
    //            if (markers[i].title === filteredSystems[j].title){
    //                markers[i].setMap(null);
    //            }
    //        }
    //    }
    //}

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
            var data = json_ob[i];
            if (data.lat && data.lng) {
                addMarker(data);
            }
        }
    }
    initializeMap();
});