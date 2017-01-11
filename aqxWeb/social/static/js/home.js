"use strict";

(function () {
    // AJAX call to fetch the profile picture and google plus account link from google account
    function fetchProfilePicture() {
	    var access_token=localStorage.getItem('access_token');
        var google_id = $('#googleId').val();
        console.debug('google id fetched: ' + google_id);

	    $.ajax({
		    url: "https://www.googleapis.com/plus/v1/people/" + google_id + "?access_token=" + access_token,
            success: function (response) {
                var imageURL="static/images/default_profile_pic.png";
                var googleImageURL = response.image.url;
                var relativeURL = googleImageURL.split("?");
                if (relativeURL.length > 0){
                    imageURL = relativeURL[0];
                }
                $('#userImage').attr('src', imageURL);
                $('#profileLink').attr('href', response.url);
            }
        });
    }

    $(document).ready(function() {
	    fetchProfilePicture();
    });
}());
