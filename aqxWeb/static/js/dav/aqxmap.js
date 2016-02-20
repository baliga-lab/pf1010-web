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
     * @param dataPoint - An Object(dict) that represents an Aquaponics System
     */
    function addMarker(dataPoint) {
        // Set the marker's location and infoWindow content
        var latLng = new google.maps.LatLng(dataPoint.lat, dataPoint.lng);
        var content = buildContentString(dataPoint);
        marker1 = new google.maps.Marker({
            title: dataPoint.title,
            position: latLng,
            map: map,
            content: content
        });

        // Add a listener for mouseover events that opens an infoWindow for the system
        google.maps.event.addListener(marker1, 'mouseover', (function (marker1, content) {
            return function () {
                infoWindow.setContent(content);
                infoWindow.open(map, marker1);
            }
        })(marker1, content));

        // Add a listener that closes the infoWindow when the mouse moves away from the marker
        google.maps.event.addListener(marker1, 'mouseout', (function () {
            return function () {
                infoWindow.close();
            }
        })(marker1));
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