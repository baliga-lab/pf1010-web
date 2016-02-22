/**
 * Created by Brian on 2/14/2016.
 */

/**
 * An Icon that represents selected system Markers
 * @type {{url: string, scaledSize: google.maps.Size}}
 */
var starredIcon = {
    url: "http://maps.google.com/mapfiles/kml/paddle/orange-stars.png",
    scaledSize: new google.maps.Size(33, 33)
};
/**
 * The default Icon for system Markers
 * @type {{url: string, scaledSize: google.maps.Size}}
 */
var defaultIcon = {
    url: "http://maps.google.com/mapfiles/kml/paddle/red-circle.png",
    scaledSize: new google.maps.Size(33, 33)
};

/**
 * Generates the HTML content of a Marker's InfoWindow
 *
 * @param system An Object(dict) that represents an Aquaponics System
 * @return {String} The HTML that populates a System's InfoWindow
 */
var buildContentString = function(system) {
    var name = system.system_name == null ? "Not available" : system.system_name;
    var technique = system.aqx_technique_name == null ? "Not available" : system.aqx_technique_name;
    var organism = system.organism_name == null ? "Not availalble" : system.organism_name;
    var growbed = system.growbed_media == null ? "Not available" : system.growbed_media;
    var crop = system.crop_name == null ? "Not available" : system.crop_name;

    return "<h2>" + name + "</h2>" +
        "<ul><li>Aquaponics Technique: " + technique + "</li>" +
        "<li>Aquatic organism: " + organism+ "</li>" +
        "<li>Growbed Medium: " + growbed + "</li>" +
        "<li>Crop: " + crop + "</li></ul>";
};

/**
 * Populates dropdown menus for each metadata category
 *
 * @param key
 * Identifies a metadata category that will populate the dropdown
 * @param elementId
 * Identifies the dropdown to populate
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

/**
 * Populates the given CheckList with the names of all visible Markers
 *
 * @param systems_and_info_object - Object containing systems and their metadata
 * @param elementID - ID of the checklist to populate
 */
var populateCheckList = function(systems_and_info_object, elementID){
    var checkList = document.getElementById(elementID);
    checkList.innerHTML = "";
    _.each(systems_and_info_object, function(system) {
        if (system.marker.getVisible()) {
            checkList.innerHTML +=  "<li><input id=\"" + system.system_uid + "\" type=\"checkbox\" value=\"" + system.system_name + "\">"
                + system.system_name + "</li>";
        }
    });
};

/**
 * Resets all markers to a visible state, and resets dropdowns
 * to their default values.
 */
function reset() {

    // Sets all markers as visible and gives them the default Marker icon
    _.each(system_and_info_object, function(system) {
        system.marker.setVisible(true);
        system.marker.setIcon(defaultIcon);
    });

    // Now that all markers are visible, repopulate the checklist
    populateCheckList(system_and_info_object, "listOfUserSystems");

    // For each dropdown, reset them to their default values
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
 * Prepares the page by initializing the Map and populating it with Markers,
 * then populates the metadata dropdowns, and the checklist of visible system names
 *
 * @param system_and_info_object - Object containing systems and their metadata
 * @param meta_data_object -  Object containing all unique metadata values
 */
var main = function(system_and_info_object, meta_data_object) {
    var map;

    /**
     * Creates a marker at a given system's lat/lng, sets its infoWindow content
     * based on the system's metadata, and adds mouseover, mouseout, and click
     * event Listeners to show the infoWindow, close it, and select the Marker,
     * respectively
     *
     * @param system An Object(dict) that represents an Aquaponics System
     *
     */
    function addMarker(system, oms) {

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
        // Add Marker to this System
        system.marker = marker;


        var flipIcons = function(marker, systemID) {
            if (marker.getIcon().url === defaultIcon.url) {
                marker.setIcon(starredIcon);
                $("#" + systemID).prop("checked", false);
                marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
            }
            else {
                marker.setIcon(defaultIcon);
                $("#" + systemID).prop("checked", false);
                marker.setZIndex(google.maps.Marker.MIN_ZINDEX);
            }
        };

        //oms.addListener('click', function(marker, event) {
        //    //flipIcons(marker, system.system_uid);
        //    if (marker.getIcon().url === defaultIcon.url) {
        //        marker.setIcon(starredIcon);
        //        $("#" + system.system_uid).prop("checked", false);
        //        marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
        //    }
        //    else {
        //        marker.setIcon(defaultIcon);
        //        $("#" + system.system_uid).prop("checked", false);
        //        marker.setZIndex(google.maps.Marker.MIN_ZINDEX);
        //    }
        //});

        oms.addListener('spiderfy', function(marker, event) {
            if (marker.getIcon().url === defaultIcon.url) {
                marker.setIcon(starredIcon);
                $("#" + system.system_uid).prop("checked", false);
                marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
            }
            else {
                marker.setIcon(defaultIcon);
                $("#" + system.system_uid).prop("checked", false);
                marker.setZIndex(google.maps.Marker.MIN_ZINDEX);
            }
            //flipIcons(marker, system.system_uid);
        });

        oms.addMarker(marker);

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

        // Add a listener that flips the Icon style of the marker on click
        google.maps.event.addListener(marker, 'click', (function (marker) {
            return function () {
                //flipIcons(marker, system.system_uid);
                if (marker.getIcon().url === defaultIcon.url){
                    marker.setIcon(starredIcon);
                    marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
                    $("#" +system.system_uid).prop("checked", true);
                }
                else{
                    marker.setIcon(defaultIcon);
                    marker.setZIndex(google.maps.Marker.MIN_ZINDEX);
                    $("#" +system.system_uid).prop("checked", false);
                }
            }
        })(marker));
    }

    /**
     * Initializes a Google Map
     * The map is centered at ISB, but zoomed to show all of North America
     * Also populates the map with a marker for each System
     */
    function initializeMap() {
        var defaultCenter = {lat: 47.622577, lng: -122.337436};
        var defaultZoom = 3;

        // Initialize and configure map with the given zoom and center
        map = new google.maps.Map(document.getElementById('map'), {
            zoom: defaultZoom,
            center: defaultCenter
        });

        var oms = new OverlappingMarkerSpiderfier(map, {markersWontMove : true, keepSpiderfied : true});

        // Create a global InfoWindow
        infoWindow = new google.maps.InfoWindow();

        // Adds each Maker to the Map
        // Technically, each Marker has a map attribute, and this is adding the
        // globally defined map above to each marker generated from the systems JSON
        _.each(system_and_info_object, function(system_and_info) {
            addMarker(system_and_info, oms);
        });
    }
    initializeMap();

    // Populate our dropdowns
    populateDropdown("aqx_techniques", "selectTechnique", meta_data_object);
    populateDropdown("aqx_organisms", "selectOrganism", meta_data_object);
    populateDropdown("growbed_media", "selectGrowbedMedium", meta_data_object);
    populateDropdown("crops", "selectCrop", meta_data_object);

    // Populate the checklist
    // All systems are visible at this point, so this list contains each system name
    populateCheckList(_.sortBy(system_and_info_object,'system_name'), "listOfUserSystems");
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

    // Repopulate the checklist so only visible systems appear
    populateCheckList(system_and_info_object, "listOfUserSystems");
};

/**
 * Whenever a checklist item is checked or unchecked, alter the marker icons
 * to display the yellow star marker for checked items, and default marker
 * for unchecked items
 * @type {*|jQuery}
 */
$('#listOfUserSystems').change(function() {

    // Generate the list of selected System Names
    var checkedNames = [];
    _.each($('#listOfUserSystems input:checked'), function(checkedInput){
        checkedNames.push(checkedInput.value);
    });

    // For each System, if its name is in the checkedNames list, give it the star Icon
    // otherwise ensure it has the default Icon
    _.each(system_and_info_object, function (system) {
        if (_.contains(checkedNames, system.system_name)) {
            system.marker.setIcon(starredIcon);
            system.marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
        }else{
            system.marker.setIcon(defaultIcon);
            system.marker.setZIndex(google.maps.Marker.MIN_ZINDEX);
        }
    });
});