"use strict";

/**
 * An Icon that represents selected system Markers
 * @type {{url: string, scaledSize: google.maps.Size}}
 */
var SELECTED_ICON = {
    url: "https://maps.google.com/mapfiles/kml/paddle/orange-stars.png",
    scaledSize: new google.maps.Size(40, 40)
};
/**
 * The default Icon for system Markers
 * @type {{url: string, scaledSize: google.maps.Size}}
 */
var DEFAULT_ICON = {
    url: "https://maps.google.com/mapfiles/kml/paddle/red-circle.png",
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
var SELECT_SYSTEM_STATUS = "selectStatus";
var MOUSEOVER = 'mouseover';
var CLICK = 'dblclick';
var CLUSTER_CLICK = 'clusterclick';
var MOUSEOUT = 'mouseout';
var SELECTED = 'selected';
var MIN_CLUSTER_ZOOM = 15;
var MAX_SYSTEM_SELECTED = 4;
var INFO_WINDOW_TIMEOUT = '2000';

// Markerclusterer and OverlappingMarkerSpiderfier need global scope
var MC;
var OMS;
var MAP;

/**
 * Returns true if the given marker has the "starred" icon
 * @param marker Any system Marker
 * @returns {boolean}
 */
function markerIsStarred(marker){
    return _.isEqual(marker.getIcon().url,SELECTED_ICON.url);
}

/**
 * Generates the HTML content of a Marker's InfoWindow
 *
 * @param system An Object(dict) that represents an Aquaponics System
 * @return {String} The HTML that populates a System's InfoWindow
 */
function buildContentString(system) {
    var name = _.isNull(system.system_name) ? NOT_AVAILABLE : system.system_name;
    var technique = _.isNull(system.aqx_technique_name) ? NOT_AVAILABLE : system.aqx_technique_name;
    var organism = _.isNull(system.organism_name) ? NOT_AVAILABLE : system.organism_name;
    var growbed = _.isNull(system.growbed_media) ? NOT_AVAILABLE : system.growbed_media;
    var crop = _.isNull(system.crop_name) ? NOT_AVAILABLE : system.crop_name;
    var redirectLink = "/system/" + system.system_uid + "/overview";

    return "<h2>" + name + "</h2>" +
        "<ul><li>Aquaponics Technique: " + technique + "</li>" +
        "<li>Aquatic organism: " + organism+ "</li>" +
        "<li>Growbed Medium: " + growbed + "</li>" +
        "<li>Crop: " + crop + "</li>" +
        "<li><a href="+redirectLink+">System Overview</a></li></ul>";
}




/**
 * Flips the current Marker icon from SELECTED_ICON to DEFAULT_ICON
 * and vice versa. Used to "select" and "de-select" markers.
 * Also, puts the display priority to the maximum if the icon is starred
 *
 * @param marker A Marker object representing a system
 * @param systemID The System_UID for the system represented by marker
 */
function flipIcons(marker, systemID) {
    var selectedSystems = getSelectedSystemIds();
    if(selectedSystems.length >= MAX_SYSTEM_SELECTED && !markerIsStarred(marker)) {
        $('#alert_placeholder').html(getAlertHTMLString("You can select up to " + MAX_SYSTEM_SELECTED + " systems", 'danger'));
    } else {
        $('#alert_placeholder').empty();
        if (!markerIsStarred(marker)) {
            marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
            marker.setIcon(SELECTED_ICON);
            setSelectedValues(systemID);
        } else {
            marker.setZIndex(google.maps.Marker.MIN_ZINDEX);
            marker.setIcon(DEFAULT_ICON);
            removeSelectedValues(systemID);
        }
        $('#analyzeSystem').trigger('chosen:updated');
    }
}

/**
 * Resets all markers to a visible state, and resets dropdowns
 * to their default values.
 */
function reset() {

    // AnalyzeSystem dropdown values has to be flushed before resetting the marker property
    clearAnalyzeDropdown();

     _.each(system_and_info_object, function(system) {
        system.marker.setVisible(true);
        system.marker.setIcon(DEFAULT_ICON);
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

    $('#selectStatus option').prop(SELECTED, function() {
        return this.defaultSelected;
    });

    filterSystemsBasedOnDropdownValues();
}

/**
 * Prepares the page by initializing the Map and populating it with Markers,
 * then populates the metadata dropdowns, and the checklist of visible system names
 *
 * @param system_and_info_object - Object containing systems and their metadata
 */
function main(system_and_info_object) {
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
                setTimeout(function(){
                    infoWindow.close();
                }, INFO_WINDOW_TIMEOUT);

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

    filterSystemsBasedOnDropdownValues();

    $('#alert_placeholder').empty();


    $('#analyzeSystem').chosen({
        max_selected_options: MAX_SYSTEM_SELECTED,
        no_results_text: "Oops, nothing found!",
        width: "95%"
    });
    $('#analyzeSystem').on('change', function(e) {
       updateMarkerIconForSelectedSystemsOnMap();
    });
    $('#analyzeSystem').bind("chosen:maxselected", function () {
        $('#alert_placeholder').html(getAlertHTMLString("You can select up to " + MAX_SYSTEM_SELECTED + " systems", 'danger'));
    });
}

/**
 * Given a system, compares its metadata with the values from the four metadata dropdowns
 * and returns true if there is a match, false otherwise
 * @param system An Aquaponics system plus its metadata values
 * @param ddAqxTech The value from Aquaponics Technique dropdown
 * @param ddAqxOrg The value from Aquatic Organism dropdown
 * @param ddAqxCrop The value from Crop name dropdown
 * @param ddAqxMedia The value from Growbed Media dropdown
 * @param ddStatus The value from Status dropdown
 * @returns {boolean}
 */
function systemMetadataDoesNotMatchesAnyDropdown(system, ddAqxTech, ddAqxOrg, ddAqxCrop, ddAqxMedia, ddStatus){
    return ((!_.isEmpty(ddAqxTech) && !_.isEqual(system.aqx_technique_name, ddAqxTech)) ||
            (!_.isEmpty(ddAqxOrg) && !_.isEqual(system.organism_name, ddAqxOrg)) ||
            (!_.isEmpty(ddAqxCrop) && !_.isEqual(system.crop_name, ddAqxCrop)) ||
            (!_.isEmpty(ddAqxMedia) && !_.isEqual(system.growbed_media, ddAqxMedia)) ||
            (!_.isEmpty(ddStatus) && !_.isEqual(system.status, ddStatus)));
}

/**
 * Used to display a notification message to the users
 * @param alertText - Notification text
 * @param type - 'Danger' or 'Success'
 * @returns {string}
 */
function getAlertHTMLString(alertText, type){
    return '<div class="alert alert-' + type + '"><a class="close" data-dismiss="alert">×</a><span>' +alertText + '</span></div>';
}

/**
 * Updates the systems displayed in Map based on filtering criteria
 */
function filterSystemsBasedOnDropdownValues() {
    var ddAqxTech = document.getElementById(SELECT_TECHNIQUE).value;
    var ddAqxOrg = document.getElementById(SELECT_ORGANISM).value;
    var ddAqxCrop = document.getElementById(SELECT_CROP).value;
    var ddAqxMedia = document.getElementById(SELECT_GROWBED_MEDIUM).value;
    var ddStatus = document.getElementById(SELECT_SYSTEM_STATUS).value;
    var filteredSystemsCount = 0;
    var mySystems = [];
    var otherUserSystems = [];
    var selectedSystemIds = getSelectedSystemIds();

    clearAnalyzeDropdown();
    _.each(_.sortBy(system_and_info_object,'system_name'), function(system) {
        if (systemMetadataDoesNotMatchesAnyDropdown(system, ddAqxTech, ddAqxOrg, ddAqxCrop, ddAqxMedia, ddStatus)){
            selectedSystemIds = _.reject(selectedSystemIds, function (id) {
                return _.isEqual(id, system.system_uid);
            });
            system.marker.setVisible(false);
        } else {
            MAP.panTo(system.marker.position);
            system.marker.setVisible(true);
            filteredSystemsCount++;
            if(_.isEqual(system.user_id, session_userId)) {
                mySystems.push(system);
            } else {
                otherUserSystems.push(system)
            }
        }
    });

    if (filteredSystemsCount > 0){
        $('#alert_placeholder').html(getAlertHTMLString("Found "+ filteredSystemsCount + " systems based on filtering criteria.", 'success'));
    }else {
        $('#alert_placeholder').html(getAlertHTMLString("No system(s) found. Please select a different filtering criteria and try again.", 'danger'));
    }

    populateAnalyzeDropdown(mySystems, otherUserSystems, selectedSystemIds);
    // Repaint clustered markers now that we've filtered
    MC.repaint();
}

/**
 * Adds the given system to analyze dropdown and sets the selected systems in dropdown
 * @param mySystems - LoggedIn user's systems
 * @param otherUserSystems - Other users systems
 * @param selectedSystemIds - Selected System Ids from dropdown
 */
function populateAnalyzeDropdown(mySystems, otherUserSystems, selectedSystemIds) {
    selectedSystemIds = _.uniq(selectedSystemIds);
    if(mySystems.length > 0) {
        var mySystemOpt = $("<optgroup label='My systems'></optgroup>");
        _.each(mySystems, function(system) {
            mySystemOpt.append($("<option>").attr('value',system.system_uid).text(system.system_name));
        });
        var userSystemOpt = $("<optgroup label='Other systems'></optgroup>");
        _.each(otherUserSystems, function(system) {
            userSystemOpt.append($("<option>").attr('value',system.system_uid).text(system.system_name));
        });
        $('#analyzeSystem').append(mySystemOpt, userSystemOpt);
    } else {
        _.each(otherUserSystems, function(system) {
            $('#analyzeSystem').append($("<option>").attr('value',system.system_uid).text(system.system_name));
        });
    }
    $('#analyzeSystem').trigger("chosen:updated");
    _.each(selectedSystemIds, function(id) {
        setSelectedValues(id)
    });
}

/**
 * @param systemId
 * Marks the systemId as selected in dropdown
 */
function setSelectedValues(systemId) {
    $('#analyzeSystem option[value='+systemId+']').prop('selected', true);
    $('#analyzeSystem').trigger("chosen:updated");
}

/**
 * @param systemId
 * Deselects the given systemId from dropdown
 */
function removeSelectedValues(systemId) {
    $('#analyzeSystem option[value='+systemId+']').removeAttr('selected');
    $('#analyzeSystem').trigger("chosen:updated");
}

/**
 * Clear analyzeSystem dropdown selection and values
 */
function clearAnalyzeDropdown() {
    $('#analyzeSystem').empty();
    $('#analyzeSystem').trigger('chosen:updated');
}

/**
 * Returns an array
 *  - EmptyArray - if no systems are selected in the dropdown OR
 *  - Selected SystemIds from dropdown
 */
function getSelectedSystemIds() {
    var systemIds = $('#analyzeSystem').val();
    return _.isNull(systemIds) ? [] : systemIds;

}

/**
 * Change the marker icon to "Selected" or "Default" in Map
 */
function updateMarkerIconForSelectedSystemsOnMap() {
    var selectedSystemIds =  getSelectedSystemIds();
    if(selectedSystemIds.length <= MAX_SYSTEM_SELECTED) {
        $('#alert_placeholder').empty();
    }
    // For each System, if its ID is in the selectedSystemId list, give it the star Icon
    // otherwise ensure it has the default Icon
    _.each(system_and_info_object, function (system) {
        if (_.contains(selectedSystemIds, system.system_uid)) {
            system.marker.setIcon(SELECTED_ICON);
            system.marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
        } else {
            system.marker.setIcon(DEFAULT_ICON);
            system.marker.setZIndex(google.maps.Marker.MIN_ZINDEX - 1);
        }
    });
}

/**
 * When user clicks analyze, check if the user has selected atleast 1 system to analyze and then save those systemIds
 * before submitting the action
 */
$('#analyzeOptions').on('submit',function() {
    var systemsSelectedToAnalyze = getSelectedSystemIds();
    if(systemsSelectedToAnalyze.length <= 0) {
        $('#alert_placeholder').html(getAlertHTMLString("Please select systems from checkbox to analyze.", 'danger'));
        return false;
    }
    var selectedSystems = systemsSelectedToAnalyze.join(",");
    document.getElementById("selectedSystems").value = JSON.stringify(selectedSystems);
    document.getElementById("systemStatus").value = document.getElementById(SELECT_SYSTEM_STATUS).value;
});