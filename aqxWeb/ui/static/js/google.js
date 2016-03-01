function onSignIn(googleUser) {
    var profile = googleUser.getBasicProfile();
    console.log('ID: ' + profile.getId());
    console.log('Name: ' + profile.getName());
    console.log('Image URL: ' + profile.getImageUrl());
    console.log('Email: ' + profile.getEmail());
    // This is what should be sent to the server
    var idtoken = googleUser.getAuthResponse().id_token;
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/signin');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function () {
        if (xhr.responseText === 'ok') {
            console.log('Signed in !');
            window.location = '/home';
        } else {
            var auth2 = gapi.auth2.getAuthInstance();
            auth2.signOut();
            alert("This application is currently in the early testing phase. Only a few users are authorized to access.");
            console.log('Error logging in');
        }
    };
    xhr.send('idtoken=' + idtoken);
}

function onLoad() {
    gapi.load('auth2', function () {
        gapi.auth2.init();
    });
}

function signOut() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/signout');
    xhr.onload = function () {
        var auth2 = gapi.auth2.getAuthInstance();
        auth2.signOut().then(function () {
            console.log('user signed out.');
            window.location = '/';
        });
    }
    xhr.send(null);
}