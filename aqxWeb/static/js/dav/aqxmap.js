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

// When the Reset button is clicked, resets the contents of the dropdowns
// TODO: Will also be used to reset the map Markers, and to clear the filter criteria.
$('#resetbtn').click(function(){
    $('#selectTechnique').val("Choose an Aquaponics Technique");
    $('#selectOrganism').val("Choose an Aquatic Organism");
    $('#selectCrop').val("Choose a Crop");
    $('#selectGrowbedMedium').val("Choose a Growbed Medium");
});

/**
 *
 * @param key - Identifies a metadata category that will populate the dropdown
 * @param elementId - Identifies the dropdown to populate
 */
var populateDropdown = function(key, elementId){
    var select = document.getElementById(elementId);
    for (value in meta_data_object[key]){
        var opt = meta_data_object[key][value];
        var el = document.createElement("option");
        el.textContent = opt;
        el.value = opt;
        select.appendChild(el);
    }
};

var main = function(system_and_info_object, meta_data_object) {
    var map;

    // Populate out dropdowns.
    populateDropdown("aqx_techniques", "selectTechnique");
    populateDropdown("aqx_organisms", "selectOrganism");
    populateDropdown("growbed_media", "selectGrowbedMedium");
    populateDropdown("crops", "selectCrop");

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
            content: content
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
        for (item in system_and_info_object){
            addMarker(system_and_info_object[item]);
        }
    }
    initializeMap();
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
        if((!_.isEmpty(dp1) && system.aqx_technique_name != dp1) || (!_.isEmpty(dp2) && system.organism_name != dp2) || (!_.isEmpty(dp3) &&system.crop_name != dp3) || (!_.isEmpty(dp4) && system.growbed_media != dp4)) {
            system.marker.setVisible(false);
        } else {
            system.marker.setVisible(true);
        }
    });
};


function reset() {
     _.each(system_and_info_object, function(system) {
         system.marker.setVisible(true);
     });
};

function filterSystemsBasedOnSelectedUser() {
    // Gets an array of checked checkboxes
    var checkedItems = $('#listOfUserSystems input:checked');

    if(checkedItems.length > 0) {
        // Set visibility for all the systems to false
        _.each(system_and_info_object, function(system) {
            system.marker.setVisible(false);
        });
        // Set visible = true only for checked items
         _.each(checkedItems, function(item) {
            _.each(system_and_info_object, function(system) {
                if(system.system_name === item.value)
                    system.marker.setVisible(true);
            });
        });
    } else if(checkedItems.length == 0) {
        _.each(system_and_info_object, function(system) {
            system.marker.setVisible(true);
        });
    }
};
