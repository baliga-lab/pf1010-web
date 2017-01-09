"use strict";

var aqx_editsystem;
if (!aqx_editsystem) {
    aqx_editsystem = {};
}

// This is our form controller based solely on jQuery instead of
// Angular 1
(function () {

    function storeSocial(userID, systemID, systemUID, systemName, location, status) {
        var socSystem = {
            'user': userID,
            'system': {
                'system_id': systemID,
                'system_uid': systemUID,
                'name': systemName,
                'description': systemName,
                'location_lat': location.lat,
                'location_lng': location.lng,
                'status': status
            }
        };
        $.ajax({
            type: 'POST',
            url: '/social/aqxapi/v1/system',
            data: JSON.stringify(socSystem),
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                console.log('yes, success: ' + data);
                window.location.href = '/system/' + systemUID + '/measurements';
            },
            dataType: 'json'
        });
    }

    aqx_editsystem.create = function() {
        var data = $('#create_form').serializeArray();
        var submitData = { 'location': {}, 'gbMedia': [{'ID': 0}],
                           'crops': [{'ID': 0, 'count': 0}],
                           'organisms': [{'ID': 0, 'count': 0}] };
        // Translate into JSON for the backend API
        for (var i = 0; i < data.length; i++) {
            var obj = data[i];
            if (obj.name == 'name') submitData['name'] = obj.value;
            if (obj.name == 'startDate') submitData['startDate'] = obj.value;
            if (obj.name == 'location.lat') submitData['location']['lat'] = obj.value;
            if (obj.name == 'location.lng') submitData['location']['lng'] = obj.value;
            if (obj.name == 'techniqueID') submitData['techniqueID'] = obj.value;
            if (obj.name == 'gbMediaID') submitData['gbMedia'][0]['ID'] = obj.value;
            if (obj.name == 'cropID') submitData['crops'][0]['ID'] = obj.value;
            if (obj.name == 'cropCount') submitData['crops'][0]['count'] = obj.value;
            if (obj.name == 'organismID') submitData['organisms'][0]['ID'] = obj.value;
            if (obj.name == 'organismCount') submitData['organisms'][0]['count'] = obj.value;
        }
        $.ajax({
            type: 'POST',
            url: '/aqxapi/v2/system',
            data: JSON.stringify(submitData),
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                console.log('yes, success: ' + data);
                storeSocial(data.userID, data.systemID, data.systemUID,
                            submitData['name'], submitData['location'],
                            100);
            },
            dataType: 'json'
        });
        return false;
    }

    function address_to_geocode(address) {
        var geocoder = new google.maps.Geocoder();
        geocoder.geocode({ 'address': address }, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                $('#sysloclat').val(results[0].geometry.location.lat());
                $('#sysloclng').val(results[0].geometry.location.lng());
            }
            else {
                alert("Geocode was not successful for the following reason: " + status);
            }
        });
    };

    $(document).ready(function() {
        $('#get_geocoords').click(function () {
            address_to_geocode($("input[name='address']").val());
        });
        $('#create_form').submit(aqx_editsystem.create);
    });

}());
