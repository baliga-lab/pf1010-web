/**
 * Created by Brian on 2/14/2016.
 */

$(document).ready(function() {

    var map;

    /**
     *
     * @param key - Identifies a metadata category that will populate the dropdown
     * @param elementId - Identifies the dropdown to populate
     */
    function populateDropdown(key, elementId){
        var select = document.getElementById(elementId);
        for(var i = 0; i < meta_data_object[key].length; i++) {
            var opt = meta_data_object[key][i];
            var el = document.createElement("option");
            el.textContent = opt;
            el.value = opt;
            select.appendChild(el);
        }
    };

    // Populate out dropdowns. This might get moved to the html.
    populateDropdown("aqx_techniques", "selectTechnique");
    populateDropdown("aqx_organisms", "selectOrganism");
    populateDropdown("growbed_media", "selectGrowbedMedium");
    populateDropdown("crops", "selectCrop");

    /**
     *
     * @param dataPoint - An Object(dict) that represents an Aquaponics System
     * @returns {string} - HTML that populates a System's InfoWindow
     */
    function buildContentString(dataPoint) {
        return "<h2>" + dataPoint.system_name + "</h2>" +
            "<ul><li>Aquaponics Technique: " + dataPoint.aqx_technique_name + "</li>" +
            "<li>Aquatic organism: " + dataPoint.organism_name + "</li>" +
            "<li>Growbed Medium: " + dataPoint.growbed_media + "</li>" +
            "<li>Crop: " + dataPoint.crop_name + "</li></ul>";
    }

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

        // Add the marker to a list.
        // TODO: Can we refactor this so we're only storing the list of markers to remove
        markers.push(marker1);
    }

    // Naive implementation to filter out markers
    // TODO: Implement a quicker way to filter these.
    //function removeFilteredMarkers(filteredSystems){
    //    for (var i = 0; i < markers.length; i++) {
    //        for (var j = 0; j < filteredSystems.length; j++){
    //            if (markers[i].title === filteredSystems[j].title){
    //                markers[i].setMap(null);
    //            }
    //        }
    //    }
    //}

    function resetMarkers(){
         for (var i = 0, length = markers.length; i < length; i++) {
            markers[i].setMap(map);
        }
    }

    /**
     * Initializes a Google Map
     */
    function initializeMap() {
        var defaultCenter = {lat: 47.622577, lng: -122.337436};
        var defaultZoom = 3;

        // Set map config
        map = new google.maps.Map(document.getElementById('map'), {
            zoom: defaultZoom,
            center: defaultCenter
        });

        // Create infowindow global class
        infoWindow = new google.maps.InfoWindow();

        // Add map to markers
        for (var i = 0, length = system_and_info_object.length; i < length; i++) {
            addMarker(system_and_info_object[i]);
        }
    }
    initializeMap();
});