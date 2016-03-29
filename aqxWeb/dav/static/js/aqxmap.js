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
var MAPDIV = 'map';
var OPTION = 'option';
var NOT_AVAILABLE = 'Not available';
var LIST_OF_USER_SYSTEMS = "listOfUserSystems";
var SELECT_TECHNIQUE = "selectTechnique";
var SELECT_ORGANISM = "selectOrganism";
var SELECT_CROP = "selectCrop";
var SELECT_GROWBED_MEDIUM = "selectGrowbedMedium";
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
var MC;
var OMS;
var MAP;

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
    var name = _.isNull(system.system_name) ? NOT_AVAILABLE : system.system_name;
    var technique = _.isNull(system.aqx_technique_name) ? NOT_AVAILABLE : system.aqx_technique_name;
    var organism = _.isNull(system.organism_name) ? NOT_AVAILABLE : system.organism_name;
    var growbed = _.isNull(system.growbed_media) ? NOT_AVAILABLE : system.growbed_media;
    var crop = _.isNull(system.crop_name) ? NOT_AVAILABLE : system.crop_name;

    return "<h2>" + name + "</h2>" +
        "<ul><li>Aquaponics Technique: " + technique + "</li>" +
        "<li>Aquatic organism: " + organism+ "</li>" +
        "<li>Growbed Medium: " + growbed + "</li>" +
        "<li>Crop: " + crop + "</li></ul>";
};

/**
 * Populates the given CheckList with the names of all visible Markers
 *
 * @param systems_and_info_object - Object containing systems and their metadata
 * @param elementID - ID of the checklist to populate
 */
var populateCheckList = function(systems_and_info_object, elementID) {
    var checkList = document.getElementById(elementID);
    //var selectList = document.getElementById("analyzeSystems");
    checkList.innerHTML = "";
    _.each(systems_and_info_object, function(system) {
        if (system.marker.getVisible()) {
            if(markerIsStarred(system.marker)) {
                $('#analyzeSystems').dropdown('set selected', system.system_uid);
                checkList.innerHTML += getCheckListInnerHtml(system.system_uid, system.system_name, true);
            } else {
                checkList.innerHTML += getCheckListInnerHtml(system.system_uid, system.system_name, false);
            }
        }
    });
};

var addSystemToAnalyzeSystemDropdown = function(system) {
    $('#analyzeSystems').append($("<option></option>")
                        .attr("value",system.system_uid)
                        .text(system.system_name));
};
/**
 *
 * @param systemId - SystemID
 * @param systemName - System name
 * @param isChecked - Checks the checkbox
 * @returns {string}
 */
var getCheckListInnerHtml = function (systemId, systemName, isChecked) {
    var checked =  isChecked ? "checked" : "" ;
     return  "<li><input id=\"" + systemId +
             "\" type=\"checkbox\" value=\"" + systemName +
             "\"" + checked + ">" + systemName + "</li>";
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
    var selectedSystems = getAnalyzeSystemValues();
    if(selectedSystems.length >=5 && !markerIsStarred(marker)) {
        $('#alert_placeholder').html(getAlertHTMLString("You can select up to 5 systems", 'danger'));
    } else {
        $('#analyzeSystems').dropdown('clear');
        if (!markerIsStarred(marker)) {
            marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
            marker.setIcon(SELECTED_ICON);
            selectedSystems.push(systemID);
            $("#" + systemID).prop(CHECKED, true);
        } else {
            marker.setZIndex(google.maps.Marker.MIN_ZINDEX);
            marker.setIcon(DEFAULT_ICON);
            selectedSystems = _.reject(selectedSystems, function (id) {
                return _.isEqual(id, systemID);
            });
            $("#" + systemID).prop(CHECKED, false);
        }
        $('#analyzeSystems').dropdown('set selected', selectedSystems);
    }
};

/**
 * Returns selected system's Id from dropdown or []
 */
function getAnalyzeSystemValues() {
    var systemIds = $('#analyzeSystems').val();
    return _.isNull(systemIds) ? [] : systemIds;
}
/**
 * Resets all markers to a visible state, and resets dropdowns
 * to their default values.
 */
function reset() {

    // AnalyzeSystem dropdown values has to be flushed before resetting the marker property
    $('#analyzeSystems').dropdown('clear');
    $('#analyzeSystems').empty();

    // Sets all markers as visible and gives them the default Marker icon
    _.each(_.sortBy(system_and_info_object,'system_name'), function(system) {
        system.marker.setVisible(true);
        system.marker.setIcon(DEFAULT_ICON);
        addSystemToAnalyzeSystemDropdown(system);
    });

    // Repaint the clusters on reset
    MC.repaint();

    // Unspiderfy any currently spiderfied markers
    OMS.unspiderfy();

    // Now that all markers are visible, repopulate the checklist

    //populateCheckList(system_and_info_object, LIST_OF_USER_SYSTEMS);

    // Remove any active alerts
    $('#alert_placeholder').empty();

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
}

/**
 * Prepares the page by initializing the Map and populating it with Markers,
 * then populates the metadata dropdowns, and the checklist of visible system names
 *
 * @param system_and_info_object - Object containing systems and their metadata
 */
var main = function(system_and_info_object) {
    //var map;
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
            map: MAP,
            content: content,
            icon: DEFAULT_ICON,
            zIndex: google.maps.Marker.MIN_ZINDEX
        });
        // Add Marker to this System
        system.marker = marker;

        // Add marker to the OverlappingMarkerSpiderfier which handles selection of clustered Markers
        OMS.addMarker(marker);

        // Add the marker to the MarkerClusterer which handles icon display for clustered Markers
        MC.addMarker(marker);

        // Adds a listener that prevents the map from over-zooming on stacked Markers
        google.maps.event.addListener(MC, CLUSTER_CLICK, function() {
            if(MAP.getZoom() > MIN_CLUSTER_ZOOM + 1)
                MAP.setZoom(MIN_CLUSTER_ZOOM + 1);
        });

        // Add a listener for mouseover events that opens an infoWindow for the system
        google.maps.event.addListener(marker, MOUSEOVER, (function (marker, content) {
            return function () {
                infoWindow.setContent(content);
                infoWindow.open(MAP, marker);
            };
        })(marker, content));

        // Add a listener that closes the infoWindow when the mouse moves away from the marker
        google.maps.event.addListener(marker, MOUSEOUT, (function () {
            return function () {
                infoWindow.close();
            };
        })(marker));

        // Add a listener that flips the Icon style of the marker on click
        google.maps.event.addListener(marker, CLICK, (function (marker) {
            return function () {
                flipIcons(marker, system.system_uid);
            };
        })(marker));
    }

    /**
     * Initializes a Google Map
     * The map is centered at ISB, but zoomed to show all of North America
     * Also populates the map with a marker for each System
     */
    function initializeMap() {
        // Initialize and configure map with the given zoom and center
        MAP = new google.maps.Map(document.getElementById(MAPDIV), {
            zoom: DEFAULT_ZOOM,
            center: DEFAULT_CENTER
        });

        /**
         * Create an OverlappingMarkerSpiderfier(OMS) object which will manage our clustered Markers
         * @param markersWontMove Set to true, this frees OMS from having to create closures that
         *                        manage marker movements, which speeds things up a bit
         * @param keepSpiderfied Set to true so that spiderfied pins don't spontaneously close.
         *                       This setting is more conducive to allowing users to hover over
         *                       Markers to see their InfoWindows
         */
        OMS = new OverlappingMarkerSpiderfier(MAP, {markersWontMove : true, keepSpiderfied : true});
        MC = new MarkerClusterer(MAP);
        MC.setMaxZoom(MIN_CLUSTER_ZOOM);
        MC.setIgnoreHidden(true);

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

    // Populate the checklist
    // All systems are visible at this point, so this list contains each system name
    $('#analyzeSystems').dropdown({
        maxSelections: 5,
        onChange: function(value, text) {
            updateAnalyzeSystems();
        }
    });

    //populateCheckList(_.sortBy(system_and_info_object,'system_name'), LIST_OF_USER_SYSTEMS);
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
var systemMetadataDoesNotMatchesAnyDropdown = function(system, dp1, dp2, dp3, dp4){
    return ((!_.isEmpty(dp1) && system.aqx_technique_name != dp1) ||
            (!_.isEmpty(dp2) && system.organism_name != dp2) ||
            (!_.isEmpty(dp3) && system.crop_name != dp3) ||
            (!_.isEmpty(dp4) && system.growbed_media != dp4));
};

var getAlertHTMLString = function(alertText, type){
    return '<div class="alert alert-' + type + '"><a class="close" data-dismiss="alert">×</a><span>' +alertText + '</span></div>'
};

/**
 * Filter systems based on dropdown values
 */
function filterSystemsBasedOnDropdownValues() {
    var dp1 = document.getElementById(SELECT_TECHNIQUE).value;
    var dp2 = document.getElementById(SELECT_ORGANISM).value;
    var dp3 = document.getElementById(SELECT_CROP).value;
    var dp4 = document.getElementById(SELECT_GROWBED_MEDIUM).value;
    var numVisible = 0;
    $('#analyzeSystems').empty();
    _.each(_.sortBy(system_and_info_object,'system_name'), function(system) {
        if (systemMetadataDoesNotMatchesAnyDropdown(system, dp1, dp2, dp3, dp4)){
            system.marker.setVisible(false);
        } else {
            MAP.panTo(system.marker.position);
            system.marker.setVisible(true);
            addSystemToAnalyzeSystemDropdown(system);
            numVisible++;
        }
    });

    if (numVisible > 0){
        $('#alert_placeholder').html(getAlertHTMLString("Found "+ numVisible + " systems based on filtering criteria.", 'success'));
    }else {
        $('#alert_placeholder').html(getAlertHTMLString("No system(s) found. Please select a different filtering criteria and try again.", 'danger'));
    }

    // Repaint clustered markers now that we've filtered
    MC.repaint();

    // Repopulate the checklist so only visible systems appear
    //populateCheckList(system_and_info_object, LIST_OF_USER_SYSTEMS);
}

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

/**
 * Change the marker type of selected system in Map
 */
var updateAnalyzeSystems = function() {
    // Generate the list of selected System Names
    var checkedNames = getAnalyzeSystemValues();
    if(checkedNames.length <= 5) {
        $('#alert_placeholder').empty();
    }
    // For each System, if its name is in the checkedNames list, give it the star Icon
    // otherwise ensure it has the default Icon
    _.each(system_and_info_object, function (system) {
        if (_.contains(checkedNames, system.system_uid)) {
            system.marker.setIcon(SELECTED_ICON);
            system.marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
        } else {
            system.marker.setIcon(DEFAULT_ICON);
            system.marker.setZIndex(google.maps.Marker.MIN_ZINDEX - 1);
        }
    });
};



$('#analyzeOptions').on('submit',function(e) {
    var systemsSelectedToAnalyze = getAnalyzeSystemValues();
    //_.each($('#listOfUserSystems input:checked'), function(checkedInput){
    //    systemsSelectedToAnalyze.push(checkedInput.id);
    //});
    if(systemsSelectedToAnalyze.length <= 0) {
        alert("Please select systems from checkbox to analyze");
        return false;
    }
    var selectedSystems = systemsSelectedToAnalyze.join(",");
    document.getElementById("selectedSystems").value = JSON.stringify(selectedSystems);
});