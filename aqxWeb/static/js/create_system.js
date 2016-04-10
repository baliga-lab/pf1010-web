"use strict";

// Adding multiple organisms
$('#add-organism-link').click(function () {
    var html = '<div class="form-group"> \
                <label for="aqua-org">Aquatic Organism</label> \
                <select class="form-control" id="aqua-org" required> \
                    <option value="0"></option> \
                    <option value="8">Betta Fish</option> \
                    <option value="5">Blue Tilapia</option> \
                    <option value="2">Bluegill</option> \
                    <option value="7">Goldfish</option> \
                    <option value="6">Koi</option> \
                    <option value="1">Mozambique Tilapia</option> \
                    <option value="4">Nile Tilapia</option> \
                    <option value="3">Shrimp</option> \
                </select> \
            </div> \
            <div class="form-group"> \
                <input type="number" min="0" class="form-control" id="num-aqua-org" placeholder="Number of Organisms" required> \
            </div>';
    $('#add-organism').append(html);
});

// Adding multiple crops
$('#add-crop-link').click(function () {
    var html = '<div class="form-group"> \
                <label for="crop">Crop</label> \
                <select class="form-control" id="crop" required> \
                    <option value="0"></option> \
                    <option value="10">Basil</option> \
                    <option value="1">Bok Choy</option> \
                    <option value="6">Butternut Squash</option> \
                    <option value="2">Carrot</option> \
                    <option value="15">Chives</option> \
                    <option value="11">Chocolate Mint</option> \
                    <option value="13">Cilantro</option> \
                    <option value="7">Cucumber</option> \
                    <option value="16">Kale</option> \
                    <option value="12">Lemon Balm</option> \
                    <option value="14">Lemon Grass</option> \
                    <option value="3">Lettuce</option> \
                    <option value="17">Nasturtium</option> \
                    <option value="4">Pea</option> \
                    <option value="5">Strawberry</option> \
                    <option value="9">Wheatgrass</option> \
                    <option value="8">Zucchini</option> \
                </select> \
            </div> \
            <div class="form-group"> \
                <input type="number" min="1" class="form-control" id="num-crop" placeholder="Number of Crops" required> \
            </div>';
    $('#add-crop').append(html);
});

// Create system
function submit(userid) {
    var output = {
        userid: userid,
        name: $("#sys-name").val(),
        date_created: $("#start-date").val(),
        aqx_technique: $("#aqx-technique").val(),
        gb_media: $("#gb-media").val(),
        crop: $("#crop").val(),
        num_crop: $("#num-crop").val(),
        organism: $("#aqua-org").val(),
        num_org: $("#num-aqua-org").val()
    };

    var geocoder = new google.maps.Geocoder();
    geocoder.geocode( { 'address': $("#address").val()}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            output.lat = results[0].geometry.location.latitude;
            output.lng = results[0].geometry.location.longitude;
        }
        else {
            alert("Geocode was not successful for the following reason: " + status);
        }
    });

    var url = '/aqxapi/system/create';

    function onSuccess(response) {
        alert('Submission successful');
    }

    function onFailure(error) {
        alert(error);
    }

    $.post(url, output).then(onSuccess, onFailure);
}