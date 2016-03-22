// Waits Until DOM Is Ready
$(document).ready(function () {

    $("#manageSystemsTab").tabs();

});


/* function : getUserConsent
 # purpose : When the user clicks "Delete" button in the Manage Systems page, confirmation pop up appears. Only when
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

