if ("geolocation" in navigator) {
    $('.js-geolocation').show();
} else {
    $('.js-geolocation').hide();
}

// Clickable geolocation button that loads weather based on HTML5 geo-locating
$('.js-geolocation').click(function () {
    navigator.geolocation.getCurrentPosition(function (position) {
        loadWeather(position.coords.latitude + ',' + position.coords.longitude); //load weather using your lat/lng coordinates
    });
});

// Currently defaults to Seattle weather. I'm not sure of how best to do the default
// Should we just show a message saying we can't locate you?
// Or should we allow users to search cities, then get the weather that way?

$(document).ready(function () {
    loadWeather('Seattle', '');
});

function loadWeather(location, woeid) {
    $.simpleWeather({
        location: location,
        woeid: woeid,
        unit: 'f',
        success: function (weather) {
            html = '<h4>' + weather.city + ', ' + weather.region + '</h4>';
            html += '<h1 style="font-size: 42px"><img src=' + weather.thumbnail + '>' + weather.temp + ' &deg;' + weather.units.temp + '</h1>';
            //html += '<img src=' + weather.thumbnail + '>'
            html += '<p>Weather: ' + weather.currently + '</p>';
            html += '<p>Wind: ' + weather.wind.direction + ' ' + weather.wind.speed + ' ' + weather.units.speed + '</p>';
            html += '<p>High: ' + weather.high + ' Low: ' + weather.low + '</p>';
            html += '<p>Humidity: ' + weather.humidity + '%</p>';
            html += '<p>Pressure: ' + weather.pressure + '</p>';

            $("#weather").html(html);
        },
        error: function (error) {
            $("#weather").html('<p>' + error + '</p>');
        }
    });
};