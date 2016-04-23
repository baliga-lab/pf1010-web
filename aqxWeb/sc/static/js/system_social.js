// Waits Until DOM Is Ready
$(document).ready(function () {
});

/* function : getUserConsent
 # purpose : When the user clicks "Leave" button in the Systems page, confirmation pop up appears. Only when
 the user hits ok button, the user shall be removed from the system
 # params : None
 # returns : None
 */
function getUserConsent() {
    if (confirm('Are you sure?')) {
        return true;
    }
    else {
        return false;
    }
}

/* function : handleSystemCreatedTime
 # purpose : Gets the system created epoch timestamp from the system_social.html and converts it to normal time (readable
 format) and display it in the system_social.html
 # params : None
 # returns : None
 */
function handleSystemCreatedTime() {
    var epochTimeStamp = $('#systemCreatedTime').value;
    var normalTime = epochToNormalTimeStamp(epochTimeStamp);
    displaySystemCreatedTime(normalTime);

}

/* function : displaySystemCreatedTime
 # purpose : Displays the system created time (normal time) the system_social html page
 # params : normalTime
 # returns : None
 */
function displaySystemCreatedTime(normalTime) {
    $('#systemCreatedTime').text(normalTime)
}


/* function : epochToNormalTimeStamp
 # purpose : Converts epoch time stamp to normal time
 # params : epochTimeStamp
 # returns : normal time
 */
function epochToNormalTimeStamp(epochTimeStamp) {
    var dt = new Date(0); // The 0 there is the key, which sets the date to the epoch
    dt.setUTCSeconds(epochTimeStamp);
    return dt
}

/* function : renderGoogleMaps
 # purpose : Initialize & Render Google Maps With Markers Plotted Upon The Specified Latitude & Longitude
 # returns : None
 */
function renderGoogleMaps(latitude, longitude, systemName) {
    var systemLocation = new google.maps.LatLng(latitude, longitude);
    var mapDiv = document.getElementById('map');
    var infowindow = new google.maps.InfoWindow();
    var mapOptions = {
        center: systemLocation,
        zoom: 11,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    }
    var gMap = new google.maps.Map(mapDiv, mapOptions);
    // System Location Marker
    var systemLocationMarker = new google.maps.Marker({
        position: systemLocation,
        map: gMap,
        // Using the global variable which holds the boarding place name
        title: systemName,
        animation: google.maps.Animation.DROP,
        icon: 'https://maps.gstatic.com/mapfiles/ms2/micons/rangerstation.png'
    });
    google.maps.event.addListener(systemLocationMarker, 'mouseover', function () {
        infowindow.setContent(this.title);
        infowindow.open(gMap, this);
    });
}
