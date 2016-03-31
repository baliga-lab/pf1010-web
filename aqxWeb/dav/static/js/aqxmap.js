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
var NOT_AVAILABLE = 'Not available';
var SELECT_TECHNIQUE = "selectTechnique";
var SELECT_ORGANISM = "selectOrganism";
var SELECT_CROP = "selectCrop";
var SELECT_GROWBED_MEDIUM = "selectGrowbedMedium";
var MOUSEOVER = 'mouseover';
var CLICK = 'dblclick';
var CLUSTER_CLICK = 'clusterclick';
var MOUSEOUT = 'mouseout';
var SELECTED = 'selected';
var MIN_CLUSTER_ZOOM = 15;
var MAX_SYSTEM_SELECTED = 5;

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
    return _.isEqual(marker.getIcon().url,SELECTED_ICON.url);
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
 * Adds the given system to analyze dropdown
 * @param system 
 */
var addSystemToAnalyzeSystemDropdown = function(system) {
    $('#analyzeSystem').append($("<option></option>")
                        .attr("value",system.system_uid)
                        .text(system.system_name));
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
    if(selectedSystems.length >= MAX_SYSTEM_SELECTED && !markerIsStarred(marker)) {
        $('#alert_placeholder').html(getAlertHTMLString("You can select up to " + MAX_SYSTEM_SELECTED + " systems", 'danger'));
    } else {
        $('#analyzeSystem').dropdown('clear');
        if (!markerIsStarred(marker)) {
            marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
            marker.setIcon(SELECTED_ICON);
            selectedSystems.push(systemID);
        } else {
            marker.setZIndex(google.maps.Marker.MIN_ZINDEX);
            marker.setIcon(DEFAULT_ICON);
            selectedSystems = _.reject(selectedSystems, function (id) {
                return _.isEqual(id, systemID);
            });
        }
        $('#analyzeSystem').dropdown('set selected', selectedSystems);
    }
};

/**
 * Returns selected system's Id from dropdown or []
 */
function getAnalyzeSystemValues() {
    var systemIds = $('#analyzeSystem').val();
    return _.isNull(systemIds) ? [] : systemIds;
}
/**
 * Resets all markers to a visible state, and resets dropdowns
 * to their default values.
 */
function reset() {

    // AnalyzeSystem dropdown values has to be flushed before resetting the marker property
    clearAnalyzeDropdown();

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
        try {
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
            OMS = new OverlappingMarkerSpiderfier(MAP, {markersWontMove: true, keepSpiderfied: true});
            MC = new MarkerClusterer(MAP);
            MC.setMaxZoom(MIN_CLUSTER_ZOOM);
            MC.setIgnoreHidden(true);

            // Create a global InfoWindow
            infoWindow = new google.maps.InfoWindow();
        } catch(error) {
            Console.log("Error initializing google maps");
            Console.log(error.stack);
        }
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
    $('#analyzeSystem').dropdown({
        maxSelections: MAX_SYSTEM_SELECTED,
        onChange: function(value, text) {
            updateAnalyzeSystems();
        }
    });
};

/**
 * Given a system, compares its metadata with the values from the four metadata dropdowns
 * and returns true if there is a match, false otherwise
 * @param system An Aquaponics system plus its metadata values
 * @param ddAqxTech The value from the first dropdown for Aquaponics Technique
 * @param ddAqxOrg The value from the second dropdown for Aquatic Organism
 * @param ddAqxCrop The value from the third dropdown for Crop name
 * @param ddAqxMedia The value from the fourth dropdown for Growbed Media
 * @returns {boolean}
 */
var systemMetadataDoesNotMatchesAnyDropdown = function(system, ddAqxTech, ddAqxOrg, ddAqxCrop, ddAqxMedia){
    return ((!_.isEmpty(ddAqxTech) && !_.isEqual(system.aqx_technique_name, ddAqxTech)) ||
            (!_.isEmpty(ddAqxOrg) && !_.isEqual(system.organism_name, ddAqxOrg)) ||
            (!_.isEmpty(ddAqxCrop) && !_.isEqual(system.crop_name, ddAqxCrop)) ||
            (!_.isEmpty(ddAqxMedia) && !_.isEqual(system.growbed_media, ddAqxMedia)));
};

/**
 * Used to display a notification message to the users
 * @param alertText - Notification text
 * @param type - 'Danger' or 'Success'
 * @returns {string}
 */
var getAlertHTMLString = function(alertText, type){
    return '<div class="alert alert-' + type + '"><a class="close" data-dismiss="alert">×</a><span>' +alertText + '</span></div>'
};

/**
 * Updates the systems displayed in Map based on filtering criteria
 */
function filterSystemsBasedOnDropdownValues() {
    var ddAqxTech = document.getElementById(SELECT_TECHNIQUE).value;
    var ddAqxOrg = document.getElementById(SELECT_ORGANISM).value;
    var ddAqxCrop = document.getElementById(SELECT_CROP).value;
    var ddAqxMedia = document.getElementById(SELECT_GROWBED_MEDIUM).value;
    var fileteredSystemsCount = 0;

    var selectedSystems = getAnalyzeSystemValues();
    clearAnalyzeDropdown();
    _.each(_.sortBy(system_and_info_object,'system_name'), function(system) {
        if (systemMetadataDoesNotMatchesAnyDropdown(system, ddAqxTech, ddAqxOrg, ddAqxCrop, ddAqxMedia)){
            selectedSystems = _.reject(selectedSystems, function (id) {
                return _.isEqual(id, system.system_uid);
            });
            system.marker.setVisible(false);
        } else {
            MAP.panTo(system.marker.position);
            system.marker.setVisible(true);
            //selectedSystems.push(system.system_uid);
            addSystemToAnalyzeSystemDropdown(system);
            fileteredSystemsCount++;
        }
    });
     $('#analyzeSystem').dropdown('set selected', selectedSystems);
    if (fileteredSystemsCount > 0){
        $('#alert_placeholder').html(getAlertHTMLString("Found "+ fileteredSystemsCount + " systems based on filtering criteria.", 'success'));
    }else {
        $('#alert_placeholder').html(getAlertHTMLString("No system(s) found. Please select a different filtering criteria and try again.", 'danger'));
    }

    // Repaint clustered markers now that we've filtered
    MC.repaint();
}

/**
 * Clear analyzeSystem dropdown selection and values
 */
var clearAnalyzeDropdown = function() {
    $('#analyzeSystem').dropdown('clear');
    $('#analyzeSystem').empty();
}
/**
 * Change the marker icon to "Selected" or "Default" in Map
 */
var updateAnalyzeSystems = function() {
    // Generate the list of selected System Names
    var checkedNames = getAnalyzeSystemValues();
    if(checkedNames.length <= MAX_SYSTEM_SELECTED) {
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

/**
 * When user clicks analyze, check if the user has selected atleast 1 system to analyze and then save those systemIds
 * before submitting the action
 */
$('#analyzeOptions').on('submit',function() {
    var systemsSelectedToAnalyze = getAnalyzeSystemValues();
    if(systemsSelectedToAnalyze.length <= 0) {
        $('#alert_placeholder').html(getAlertHTMLString("Please select systems from checkbox to analyze.", 'danger'));
        return false;
    }
    var selectedSystems = systemsSelectedToAnalyze.join(",");
    document.getElementById("selectedSystems").value = JSON.stringify(selectedSystems);
});