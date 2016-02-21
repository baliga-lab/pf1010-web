/**
 * Created by Brian on 2/14/2016.
 */

/**
 *
 * @param dataPoint - An Object(dict) that represents an Aquaponics System
 * @returns {string} - HTML that populates a System's InfoWindow
 */
var buildContentString = function(dataPoint) {
    var name = dataPoint.system_name == null ? "Not available" : dataPoint.system_name;
    var technique = dataPoint.aqx_technique_name == null ? "Not available" : dataPoint.aqx_technique_name;
    var organism = dataPoint.organism_name == null ? "Not availalble" : dataPoint.organism_name;
    var growbed = dataPoint.growbed_media == null ? "Not available" : dataPoint.growbed_media;
    var crop = dataPoint.crop_name == null ? "Not available" : dataPoint.crop_name;

    return "<h2>" + name + "</h2>" +
        "<ul><li>Aquaponics Technique: " + technique + "</li>" +
        "<li>Aquatic organism: " + organism+ "</li>" +
        "<li>Growbed Medium: " + growbed + "</li>" +
        "<li>Crop: " + crop + "</li></ul>";
};

/**
 *
 * @param key - Identifies a metadata category that will populate the dropdown
 * @param elementId - Identifies the dropdown to populate
 */
var populateDropdown = function(key, elementId, meta_data_object){
    var select = document.getElementById(elementId);
    _.each(meta_data_object[key], function(meta_data){
        var el = document.createElement("option");
        el.textContent = meta_data;
        el.value = meta_data;
        select.appendChild(el);
    });
};
//
//var goldStar = {
//    path: 'M 125,5 155,90 245,90 175,145 200,230 125,180 50,230 75,145 5,90 95,90 z',
//    fillColor: 'yellow',
//    fillOpacity: 0.9,
//    scale: 0.1,
//    strokeColor: 'gold',
//    strokeWeight: 1
//};
var starredIcon = {
    url: "http://maps.google.com/mapfiles/kml/paddle/orange-stars.png",
    scaledSize: new google.maps.Size(33, 33)
};
var defaultIcon = {
    url: "http://maps.google.com/mapfiles/kml/paddle/red-circle.png",
    scaledSize: new google.maps.Size(33, 33) // scaled size
};

var main = function(system_and_info_object, meta_data_object) {
    var map;

    // Populate out dropdowns.
    populateDropdown("aqx_techniques", "selectTechnique", meta_data_object);
    populateDropdown("aqx_organisms", "selectOrganism", meta_data_object);
    populateDropdown("growbed_media", "selectGrowbedMedium", meta_data_object);
    populateDropdown("crops", "selectCrop", meta_data_object);

    /**
     *
     * @param system - An Object(dict) that represents an Aquaponics System
     */
    function addMarker(system) {

        // Set the marker's location and infoWindow content
        var latLng = new google.maps.LatLng(system.lat, system.lng);
        var content = buildContentString(system);
        marker = new google.maps.Marker({
            title: system.title,
            position: latLng,
            map: map,
            content: content,
            icon: defaultIcon
        });
        system.marker = marker;
        // Add a listener for mouseover events that opens an infoWindow for the system
        google.maps.event.addListener(marker, 'mouseover', (function (marker, content) {
            return function () {
                infoWindow.setContent(content);
                infoWindow.open(map, marker);
            }
        })(marker, content));

        // Add a listener that closes the infoWindow when the mouse moves away from the marker
        google.maps.event.addListener(marker, 'mouseout', (function () {
            return function () {
                infoWindow.close();
            }
        })(marker));
    }

    /**
     * Initializes a Google Map
     */
    function initializeMap() {
        var defaultCenter = {lat: 47.622577, lng: -122.337436};
        var defaultZoom = 7;

        // Set map config
        map = new google.maps.Map(document.getElementById('map'), {
            zoom: defaultZoom,
            center: defaultCenter
        });

        // Create infowindow global class
        infoWindow = new google.maps.InfoWindow();

        // Add map to markers
        _.each(system_and_info_object, function(system_and_info) {
            addMarker(system_and_info);
        });
    }
    initializeMap();
};

/**
 * Resets all markers to a visible state, and resets dropdowns
 * to their default values.
 */
function reset() {
    _.each(system_and_info_object, function(system) {
        system.marker.setVisible(true);
        system.marker.setIcon(defaultIcon);
    });
    $('#selectTechnique option').prop('selected', function() {
        return this.defaultSelected;
    });
    $('#selectOrganism option').prop('selected', function() {
        return this.defaultSelected;
    });
    $('#selectCrop option').prop('selected', function() {
        return this.defaultSelected;
    });
    $('#selectGrowbedMedium option').prop('selected', function() {
        return this.defaultSelected;
    });
};

/**
 * Filter systems based on dropdown values
 */
function filterSystemsBasedOnDropdownValues() {
    var dp1 = document.getElementById("selectTechnique").value;
    var dp2 = document.getElementById("selectOrganism").value;
    var dp3 = document.getElementById("selectCrop").value;
    var dp4 = document.getElementById("selectGrowbedMedium").value;

    _.each(system_and_info_object, function(system) {
        if((!_.isEmpty(dp1) && system.aqx_technique_name != dp1)
            || (!_.isEmpty(dp2) && system.organism_name != dp2)
            || (!_.isEmpty(dp3) &&system.crop_name != dp3)
            || (!_.isEmpty(dp4) && system.growbed_media != dp4))
        {
            system.marker.setVisible(false);
        } else {
            system.marker.setVisible(true);
        }
    });
};

$('#listOfUserSystems').change(function() {
    var checkedItems = $('#listOfUserSystems input:checked');
    console.log(checkedItems.length);

    // If a new item has had its checkbox selected
    if(checkedItems.length > 0) {
        _.each(system_and_info_object, function (system) {
            system.marker.setIcon(defaultIcon);
        });
        _.each(checkedItems, function (item) {
            console.log(item.value);
            _.each(system_and_info_object, function (system) {
                console.log(system.system_name);
                if (system.system_name === item.value) {
                    system.marker.setIcon(starredIcon);
                }
            });
        });
    }else if (checkedItems.length == 0){
        _.each(system_and_info_object, function (system) {
            system.marker.setIcon(defaultIcon);
        });
    }
});


function filterSystemsBasedOnSelectedUser() {
    // Gets an array of checked checkboxes
    var checkedItems = $('#listOfUserSystems input:checked');

    // If a new item has had its checkbox selected
    if(checkedItems.length > 0) {
        _.each(checkedItems, function (item) {
            _.each(system_and_info_object, function (system) {
                if (system.system_name === item.value) {
                    system.marker.setIcon(starredIcon);
                }
            });
        });
    }
};