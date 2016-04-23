// Waits Until DOM Is Ready
$(document).ready(function () {
});

/* function : getUserConsent
 # purpose : When the user clicks "Leave" button in the Group page, confirmation pop up appears. Only when
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
