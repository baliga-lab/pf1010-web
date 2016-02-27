/**
 * Created by Brian on 2/19/2016.
 */

/**
 *  An Icon that represents selected system Markers
 *  @type {{url: string, scaledSize: google.maps.Size}}
 */
var SELECTED_ICON = {
    url: "http://maps.google.com/mapfiles/kml/paddle/orange-stars.png",
    scaledSize: new google.maps.Size(40, 40)
};
/**
 * The default Icon for system Markers
 * @type {{url: string, scaledSize: google.maps.Size}}
 */
var DEFAULT_ICON = {
    url: "http://maps.google.com/mapfiles/kml/paddle/red-circle.png",
    scaledSize: new google.maps.Size(33, 33)
};

var dataPointOne = {aqx_technique_name : "Ebb and Flow (Media-based)",
    crop_count : "5",
    crop_name: "Strawberry",
    growbed_media: "Clay Pebbles",
    lat: "37.4142740000",
    lng: "-122.0774090000",
    organism_count: 12,
    organism_name: "Mozambique Tilapia",
    start_date: "2015-08-23",
    system_name: "My first system",
    system_uid: "316f3f2e3fe411e597b1000c29b92d09",
    user_id: 1};

var expectedHTMLOne = "<h2>My first system</h2>" +
    "<ul><li>Aquaponics Technique: Ebb and Flow (Media-based)</li>" +
    "<li>Aquatic organism: Mozambique Tilapia</li>" +
    "<li>Growbed Medium: Clay Pebbles</li>" +
    "<li>Crop: Strawberry</li></ul>";

var dataPointTwo = {aqx_technique_name : "Ebb and Flow (Media-based)",
    crop_count : "5",
    crop_name: null,
    growbed_media: "Clay Pebbles",
    lat: "37.4142740000",
    lng: "-122.0774090000",
    organism_count: 12,
    organism_name: "Mozambique Tilapia",
    start_date: "2015-08-23",
    system_name: "My first system",
    system_uid: "316f3f2e3fe411e597b1000c29b92d09",
    user_id: 1};

var expectedHTMLTwo = "<h2>My first system</h2>" +
    "<ul><li>Aquaponics Technique: Ebb and Flow (Media-based)</li>" +
    "<li>Aquatic organism: Mozambique Tilapia</li>" +
    "<li>Growbed Medium: Clay Pebbles</li>" +
    "<li>Crop: Not available</li></ul>";

var systems_and_info_mock =
{"systems":
    [
        {"system_uid": "316f3f2e3fe411e597b1000c29b92d09", "growbed_media": "Seed Starter Plugs", "crop_count": 5, "organism_count": 12, "lat": "37.4142740000", "lng": "-122.0774090000", "organism_name": "Mozambique Tilapia", "system_name": "My first system", "user_id": 1, "aqx_technique_name": "Ebb and Flow (Media-based)", "crop_name": "Strawberry", "start_date": "2015-08-23"},
        {"system_uid": "2e79ea8a411011e5aac7000c29b92d09", "growbed_media": "Coconut Coir", "crop_count": 18, "organism_count": 20, "lat": "47.6225770000", "lng": "-122.3374360000", "organism_name": "Mozambique Tilapia", "system_name": "ISB 1", "user_id": 2, "aqx_technique_name": "Floating Raft", "crop_name": "Lettuce", "start_date": "2015-08-26"}
    ]
};

var metadata_mock = {"filters": {"crops": ["Basil", "Bok Choy", "Lettuce"],
    "aqx_organisms": ["Blue Tilapia", "Koi", "Shrimp"],
    "aqx_techniques": ["Floating Raft", "Nutrient Film Technique (NFT)"],
    "growbed_media": ["Clay Pebbles", "Coconut Coir", "Seed Starter Plugs"]}};


var mapMock = new google.maps.Map(document.getElementById("map"), {
    zoom: 3,
    center: {lat: 47.622577, lng: -122.337436}
});

var markerMock = new google.maps.Marker({
    title: "Test Marker",
    position: {lat: 47.622577, lng: -122.337436},
    map: mapMock,
    content: "<h1>This is some content</h1>",
    icon: DEFAULT_ICON,
    zIndex: google.maps.Marker.MIN_ZINDEX
});

var techDpHTML = "<option value=\"\" selected=\"selected\">Choose an Aquaponics Technique</option>" +
        "<option value=\"Ebb and Flow (Media-based)\">Floating Raft</option>" +
        "<option value=\"Nutrient Film Technique (NFT)\">Nutrient Film Technique (NFT)</option>";

var organismDpHTML = "<option value=\"\" selected=\"selected\">Choose an Aquatic Organism</option>" +
        "<option value=\"Blue Tilapia\">Blue Tilapia</option>" + "<option value=\"Koi\">Koi</option>" +
        "<option value=\"Shrimp\">Shrimp</option>";
