/**
 * Created by Brian on 2/19/2016.
 */

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
