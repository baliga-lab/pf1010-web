/**
 * Created by Brian on 2/14/2016.
 */

/**
 * An Icon that represents selected system Markers
 * @type {{url: string, scaledSize: google.maps.Size}}
 */
var SELECTED_ICON = {
    url: "http://maps.google.com/mapfiles/kml/paddle/orange-stars.png",
    scaledSize: new google.maps.Size(40, 40)
};
/**
 * The default Icon for system Markers
 * @type {{url: string, scaledSize: google.maps.Size}}
 */
var DEFAULT_ICON = {
    url: "http://maps.google.com/mapfiles/kml/paddle/red-circle.png",
    scaledSize: new google.maps.Size(33, 33)
};

// Define some global constants
var DEFAULT_CENTER = {lat: 47.622577, lng: -122.337436};
var DEFAULT_ZOOM = 3;
var MAP = 'map';
var OPTION = 'option';
var NOT_AVAILABLE = 'Not available';
var LIST_OF_USER_SYSTEMS = "listOfUserSystems";
var LIST_OF_MY_SYSTEMS = "listOfMySystems";
var SELECT_TECHNIQUE = "selectTechnique";
var SELECT_ORGANISM = "selectOrganism";
var SELECT_CROP = "selectCrop";
var SELECT_GROWBED_MEDIUM = "selectGrowbedMedium";
var SPIDERFY = 'spiderfy';
var MOUSEOVER = 'mouseover';
var CLICK = 'dblclick';
var CLUSTER_CLICK = 'clusterclick';
var MOUSEOUT = 'mouseout';
var SELECTED = 'selected';
var CHECKED = 'checked';
var AQX_TECHNIQUES = "aqx_techniques";
var AQX_ORGANISMS = "aqx_organisms";
var CROPS = "crops";
var GROWBED_MEDIA = "growbed_media";
var MIN_CLUSTER_ZOOM = 15;

// Markerclusterer and OverlappingMarkerSpiderfier need global scope
var mc;
var oms;


/**
 * Returns true if the given marker has the "starred" icon
 * @param marker Any system Marker
 * @returns {boolean}
 */
var markerIsStarred = function(marker){
    return marker.getIcon().url === SELECTED_ICON.url;
};

/**
 * Generates the HTML content of a Marker's InfoWindow
 *
 * @param system An Object(dict) that represents an Aquaponics System
 * @return {String} The HTML that populates a System's InfoWindow
 */
var buildContentString = function(system) {
    var name = system.system_name == null ? NOT_AVAILABLE : system.system_name;
    var technique = system.aqx_technique_name == null ? NOT_AVAILABLE : system.aqx_technique_name;
    var organism = system.organism_name == null ? NOT_AVAILABLE : system.organism_name;
    var growbed = system.growbed_media == null ? NOT_AVAILABLE : system.growbed_media;
    var crop = system.crop_name == null ? NOT_AVAILABLE : system.crop_name;

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
        var el = document.createElement(OPTION);
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
// TODO: Look into changing this similarly to the above fxn (as per Guna). It can definitely be done, just gotta research it.
var populateCheckList = function(systems_and_info_object, elementID){
    var checkList = document.getElementById(elementID);
    checkList.innerHTML = "";
    _.each(systems_and_info_object, function(system) {
        if (system.marker.getVisible()) {
            if(markerIsStarred(system.marker)) {
                checkList.innerHTML += "<li><input id=\"" + system.system_uid
                    + "\" type=\"checkbox\" value=\"" + system.system_name + "\"checked>"
                    + system.system_name + "</li>";
            }else{
                checkList.innerHTML += "<li><input id=\"" + system.system_uid
                    + "\" type=\"checkbox\" value=\"" + system.system_name + "\">"
                    + system.system_name + "</li>";
            }
        }
    });
};

/**
 * Flips the current Marker icon from SELECTED_ICON to DEFAULT_ICON
 * and vice versa. Used to "select" and "de-select" markers.
 * Also, puts the display priority to the maximum if the icon is starred
 *
 * @param marker A Marker object representing a system
 * @param systemID The System_UID for the system represented by marker
 */
var flipIcons = function(marker, systemID) {
    if (!markerIsStarred(marker)) {
        marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
        marker.setIcon(SELECTED_ICON);
        $("#" + systemID).prop(CHECKED, true);
    }
    else {
        marker.setZIndex(google.maps.Marker.MIN_ZINDEX);
        marker.setIcon(DEFAULT_ICON);
        $("#" + systemID).prop(CHECKED, false);
    }
};

/**
 * Resets all markers to a visible state, and resets dropdowns
 * to their default values.
 */
function reset() {

    // Sets all markers as visible and gives them the default Marker icon
    _.each(system_and_info_object, function(system) {
        system.marker.setVisible(true);
        system.marker.setIcon(DEFAULT_ICON);
    });

    // Repaint the clusters on reset
    mc.repaint();

    // Unspiderfy any currently spiderfied markers
    oms.unspiderfy();

    // Now that all markers are visible, repopulate the checklist
    populateCheckList(system_and_info_object, LIST_OF_USER_SYSTEMS);

    // For each dropdown, reset them to their default values
    $('#selectTechnique option').prop(SELECTED, function() {
        return this.defaultSelected;
    });
    $('#selectOrganism option').prop(SELECTED, function() {
        return this.defaultSelected;
    });
    $('#selectCrop option').prop(SELECTED, function() {
        return this.defaultSelected;
    });
    $('#selectGrowbedMedium option').prop(SELECTED, function() {
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
    var infoWindow;

    /**
     * Creates a marker at a given system's lat/lng, sets its infoWindow content
     * based on the system's metadata, and adds mouseover, mouseout, and click
     * event Listeners to show the infoWindow, close it, and select the Marker,
     * respectively
     */
    function addMarker(system) {

        // Set the marker's location and infoWindow content
        var latLng = new google.maps.LatLng(system.lat, system.lng);
        var content = buildContentString(system);
        var marker = new google.maps.Marker({
            title: system.title,
            position: latLng,
            map: map,
            content: content,
            icon: DEFAULT_ICON,
            zIndex: google.maps.Marker.MIN_ZINDEX
        });
        // Add Marker to this System
        system.marker = marker;

        // Add marker to the OverlappingMarkerSpiderfier which handles selection of clustered Markers
        oms.addMarker(marker);

        // Add the marker to the MarkerClusterer which handles icon display for clustered Markers
        mc.addMarker(marker);

        // Adds a listener that prevents the map from over-zooming on stacked Markers
        google.maps.event.addListener(mc, CLUSTER_CLICK, function() {
            if(map.getZoom() > MIN_CLUSTER_ZOOM + 1)
                map.setZoom(MIN_CLUSTER_ZOOM + 1);
        });

        // Add a listener for mouseover events that opens an infoWindow for the system
        google.maps.event.addListener(marker, MOUSEOVER, (function (marker, content) {
            return function () {
                infoWindow.setContent(content);
                infoWindow.open(map, marker);
            }
        })(marker, content));

        // Add a listener that closes the infoWindow when the mouse moves away from the marker
        google.maps.event.addListener(marker, MOUSEOUT, (function () {
            return function () {
                infoWindow.close();
            }
        })(marker));

        // Add a listener that flips the Icon style of the marker on click
        google.maps.event.addListener(marker, CLICK, (function (marker) {
            return function () {
                flipIcons(marker, system.system_uid);
            }
        })(marker));
    }

    /**
     * Initializes a Google Map
     * The map is centered at ISB, but zoomed to show all of North America
     * Also populates the map with a marker for each System
     */
    function initializeMap() {
        // Initialize and configure map with the given zoom and center
        map = new google.maps.Map(document.getElementById(MAP), {
            zoom: DEFAULT_ZOOM,
            center: DEFAULT_CENTER
        });

        /**
         * Create an OverlappingMarkerSpiderfier object which will manage our clustered Markers
         * @param markersWontMove Set to true, this frees oms from having to create closures that
         *                        manage marker movements, which speeds things up a bit
         * @param keepSpiderfied Set to true so that spiderfied pins don't spontaneously close.
         *                       This setting is more conducive to allowing users to hover over
         *                       Markers to see their InfoWindows
         */
        oms = new OverlappingMarkerSpiderfier(map, {markersWontMove : true, keepSpiderfied : true});
        mc = new MarkerClusterer(map);
        mc.setMaxZoom(MIN_CLUSTER_ZOOM);
        mc.setIgnoreHidden(true);

        // Create a global InfoWindow
        infoWindow = new google.maps.InfoWindow();

        // Adds each Marker to the Map and OverlappingMarkerSpiderfier
        // Technically, each Marker has a map attribute, and this is adding the
        // globally defined map above to each marker generated from the systems JSON
        _.each(system_and_info_object, function(system_and_info) {
            addMarker(system_and_info);
        });
    }
    initializeMap();

    // Populate our dropdowns
    populateDropdown(AQX_TECHNIQUES, SELECT_TECHNIQUE, meta_data_object);
    populateDropdown(AQX_ORGANISMS, SELECT_ORGANISM, meta_data_object);
    populateDropdown(CROPS, SELECT_CROP, meta_data_object);
    populateDropdown(GROWBED_MEDIA, SELECT_GROWBED_MEDIUM, meta_data_object);

    // Populate the checklist
    // All systems are visible at this point, so this list contains each system name
    populateCheckList(_.sortBy(system_and_info_object,'system_name'), LIST_OF_USER_SYSTEMS);

    // Populate a placeholder checklist for logged in User's sytems
    populate_dummy_user_systems_checklist();
};

/**
 * Given a system, compares its metadata with the values from the four metadata dropdowns
 * and returns true if there is a match, false otherwise
 * @param system An Aquaponics system plus its metadata values
 * @param dp1 The value from the first dropdown for Aquaponics Technique
 * @param dp2 The value from the second dropdown for Aquatic Organism
 * @param dp3 The value from the third dropdown for Crop name
 * @param dp4 The value from the fourth dropdown for Growbed Media
 * @returns {boolean}
 */
var systemMetadataMatchesAnyDropdown = function(system, dp1, dp2, dp3, dp4){
    return ((!_.isEmpty(dp1) && system.aqx_technique_name != dp1)
    || (!_.isEmpty(dp2) && system.organism_name != dp2)
    || (!_.isEmpty(dp3) &&system.crop_name != dp3)
    || (!_.isEmpty(dp4) && system.growbed_media != dp4))
};

/**
 * Filter systems based on dropdown values
 */
function filterSystemsBasedOnDropdownValues() {
    var dp1 = document.getElementById(SELECT_TECHNIQUE).value;
    var dp2 = document.getElementById(SELECT_ORGANISM).value;
    var dp3 = document.getElementById(SELECT_CROP).value;
    var dp4 = document.getElementById(SELECT_GROWBED_MEDIUM).value;

    _.each(system_and_info_object, function(system) {
        if (systemMetadataMatchesAnyDropdown(system, dp1, dp2, dp3, dp4)){
            system.marker.setVisible(false);
        } else {
            system.marker.setVisible(true);
        }
    });

    // Repaint clustered markers now that we've filtered
    mc.repaint();

    // Repopulate the checklist so only visible systems appear
    populateCheckList(system_and_info_object, LIST_OF_USER_SYSTEMS);
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
            system.marker.setIcon(SELECTED_ICON);
            system.marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
        }else{
            system.marker.setIcon(DEFAULT_ICON);
            system.marker.setZIndex(google.maps.Marker.MIN_ZINDEX - 1);
        }
    });
});


var populate_dummy_user_systems_checklist = function(){
    var user_systems_and_info = {
        "systems":
            [
                {"system_uid": "316f3f2e3fe411e597b1000c29b92d09",
                    "growbed_media": null, "crop_count": 5, "organism_count": 12,
                    "lat": "37.4142740000", "lng": "-122.0774090000", "organism_name": "Mozambique Tilapia",
                    "system_name": "My first system", "user_id": 1,
                    "aqx_technique_name": "Ebb and Flow (Media-based)",
                    "crop_name": "Strawberry", "start_date": "2015-08-23"},
                {"system_uid": "2e79ea8a411011e5aac7000c29b92d09", "growbed_media": null, "crop_count": 18,
                    "organism_count": 20, "lat": "47.6225770000", "lng": "-122.3374360000",
                    "organism_name": "Mozambique Tilapia", "system_name": "ISB 1", "user_id": 2,
                    "aqx_technique_name": "Floating Raft", "crop_name": "Lettuce", "start_date": "2015-08-26"}
            ]
    };

    var myCheckList = document.getElementById(LIST_OF_MY_SYSTEMS);
    myCheckList.innerHTML = "";
    _.each(user_systems_and_info.systems, function(system) {
        myCheckList.innerHTML += "<li><input id=\"" + system.system_uid
            + "\" type=\"checkbox\" value=\"" + system.system_name + "\">"
            + system.system_name + "</li>";
    });
};

<<<<<<< HEAD

=======
>>>>>>> refs/remotes/origin/release_sprint2
$('#analyzeOptions').on('submit',function(e) {
    var systemsSelectedToAnalyze = [];
    _.each($('#listOfUserSystems input:checked'), function(checkedInput){
        systemsSelectedToAnalyze.push(checkedInput.id);
    });
    if(systemsSelectedToAnalyze.length <= 0) {
        alert("Please select systems from checkbox to analyze");
        return false;
    }
    var selectedSystems = systemsSelectedToAnalyze.join(",");
    document.getElementById("selectedSystems").value = JSON.stringify(selectedSystems);
});