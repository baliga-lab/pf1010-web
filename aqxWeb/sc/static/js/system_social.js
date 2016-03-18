// Waits Until DOM Is Ready
$(document).ready(function () {


});



/* function : getUserConsent
 # purpose : When the user clicks "Leave" button in the Systems page, confirmation pop up appears. Only when
  the user hits ok button, the user shall be removed from the system
 # params : None
 # returns : None
 */
function getUserConsent(){
    if (confirm('Are you sure?')) {
      return true;
    }
    else{
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