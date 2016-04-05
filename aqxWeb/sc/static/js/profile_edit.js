// Waits Until DOM Is Ready
$(document).ready(function () {
    fetchProfilePicture();
});


// AJAX call to fetch the profile picture and google plus account link from google account
function fetchProfilePicture() {
    var access_token = localStorage.getItem('access_token');
    $.ajax({
        url: "https://www.googleapis.com/plus/v1/people/me?access_token=" + access_token,
        success: function (response) {
            var imageURL = "static/images/default_profile_pic.png";
            var googleImageURL = response.image.url;
            //https://lh3.googleusercontent.com/-ipIjoUxn65w/AAAAAAAAAAI/AAAAAAAALkw/pVWAsTM12e4/photo.jpg?sz=50
            var relativeURL = googleImageURL.split("?");
            if (relativeURL.length > 0) {
                imageURL = relativeURL[0];
            }
            $('#userImage').attr('src', imageURL);
            $('#profileLink').attr('href', response.url);

        }
    });

}