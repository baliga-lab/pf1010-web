/**
 * Created by Brian on 2/14/2016.
 */

if ("geolocation" in navigator) {
  console.log("Nav");
  $('.js-geolocation').show();
} else {
  $('.js-geolocation').hide();
}

// Clickable geolocation button that loads weather based on HTML5 geo-locating
$('.js-geolocation').click(function() {
  navigator.geolocation.getCurrentPosition(function(position) {
    loadWeather(position.coords.latitude+','+position.coords.longitude); //load weather using your lat/lng coordinates
  });
});

// Currently defaults to Seattle weather. I'm not sure of how best to do the default
// Should we just show a message saying we can't locate you?
// Or should we allow users to search cities, then get the weather that way?

$(document).ready(function() {
  loadWeather('Seattle','');
});

function loadWeather(location, woeid) {
  $.simpleWeather({
    location: location,
    woeid: woeid,
    unit: 'f',
    success: function(weather) {
      //html = '<h1 style="font-size: 50px"><i class="icon-'+weather.code+'"></i> '+weather.temp+'&deg;'+weather.units.temp+'</h1>';
      html = '<h1 style="font-size: 50px"><img src=' + weather.thumbnail + '>' + weather.temp+'&deg;'+weather.units.temp+'</h1>';
      //html += '<img src=' + weather.thumbnail + '>'
      html += '<ul><li>'+weather.city+', '+weather.region+'</li>';
      html += '<li class="currently">'+weather.currently+'</li>';
      html += '<li>'+weather.wind.direction+' '+weather.wind.speed+' '+weather.units.speed+'</li>';
      html += '<li>High: '+weather.high+' Low: '+weather.low+' Humidity: '+
                weather.humidity+'% Pressure: '+weather.pressure+'</li></ul>';

      $("#weather").html(html);
    },
    error: function(error) {
      $("#weather").html('<p>'+error+'</p>');
    }
  });
};