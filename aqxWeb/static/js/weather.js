if ("geolocation" in navigator) {
    $('.js-geolocation').show();
} else {
    $('.js-geolocation').hide();
}

// Clickable geolocation button that loads weather based on HTML5 geo-locating
/*$('.js-geolocation').click(function () {
    navigator.geolocation.getCurrentPosition(function (position) {
        loadWeather(position.coords.latitude + ',' + position.coords.longitude); //load weather using your lat/lng coordinates
    });
});*/

$(document).ready(function () {
    navigator.geolocation.getCurrentPosition(function (position) {
        loadWeather(position.coords.latitude + ',' + position.coords.longitude); //load weather using your lat/lng coordinates
    });
});

function loadWeather(location, woeid) {
    $.simpleWeather({
        location: location,
        woeid: woeid,
        unit: 'f',
        success: function (weather) {
            html = '<h4>' + weather.city + ', ' + weather.region + '</h4>';
            html += '<p>Weather: ' + weather.currently + '</p>';
            html += '<h1 style="font-size: 25px"><img src=' + weather.thumbnail + '>' + weather.temp + ' &deg;' + weather.units.temp + '</h1>';
            html += '<p><small>High: ' + weather.high + ' Low: ' + weather.low + ' ';
            html += ' Wind: ' + weather.wind.direction + ' ' + weather.wind.speed + ' ' + weather.units.speed + '<br/>';
            html += 'Humidity: ' + weather.humidity + '% ';
            html += ' Pressure: ' + weather.pressure + '</small></p>';

            $("#weather").html(html);
        },
        error: function (error) {
            $("#weather").html('<p>' + error + '</p>');
        }
    });
}