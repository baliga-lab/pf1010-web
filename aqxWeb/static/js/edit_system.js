"use strict";

/*
 * Javascript support code for edit/create system forms. This includes AJAX form handling
 * as well as dynamic forms.
 */
var aqx_editsystem;
if (!aqx_editsystem) {
    aqx_editsystem = {};
}

(function () {

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
            if (obj.name == 'location.lat') submitData['location']['lat'] = parseFloat(obj.value);
            if (obj.name == 'location.lng') submitData['location']['lng'] = parseFloat(obj.value);
            if (obj.name == 'techniqueID') submitData['techniqueID'] = parseInt(obj.value);
            if (obj.name == 'gbMediaID') submitData['gbMedia'][0]['ID'] = obj.value;
            if (obj.name == 'cropID') submitData['crops'][0]['ID'] = parseInt(obj.value);
            if (obj.name == 'cropCount') submitData['crops'][0]['count'] = parseInt(obj.value);
            if (obj.name == 'organismID') submitData['organisms'][0]['ID'] = parseInt(obj.value);
            if (obj.name == 'organismCount') submitData['organisms'][0]['count'] = parseInt(obj.value);
            if (obj.name.startsWith('organismID_')) {
                var orgnum = parseInt(obj.name.substring('organismID_'.length));
                if (typeof(submitData['organisms'][orgnum]) === 'undefined') {
                    submitData['organisms'][orgnum] = {};
                }
                submitData['organisms'][orgnum]['ID'] = parseInt(obj.value);
            }
            if (obj.name.startsWith('organismCount_')) {
                var orgnum = parseInt(obj.name.substring('organismCount_'.length));
                if (typeof(submitData['organisms'][orgnum]) === 'undefined') {
                    submitData['organisms'][orgnum] = {};
                }
                submitData['organisms'][orgnum]['count'] = obj.value.length > 0 ? parseInt(obj.value) : 0;
            }
            if (obj.name.startsWith('cropID_')) {
                var cropnum = parseInt(obj.name.substring('cropID_'.length));
                if (typeof(submitData['crops'][cropnum]) === 'undefined') {
                    submitData['crops'][cropnum] = {};
                }
                submitData['crops'][cropnum]['ID'] = parseInt(obj.value);
            }
            if (obj.name.startsWith('cropCount_')) {
                var cropnum = parseInt(obj.name.substring('cropCount_'.length));
                if (typeof(submitData['crops'][cropnum]) === 'undefined') {
                    submitData['crops'][cropnum] = {};
                }
                submitData['crops'][cropnum]['count'] = obj.value.length > 0 ? parseInt(obj.value) : 0;
            }
        }
        $.ajax({
            type: 'POST',
            url: '/aqxapi/v2/system',
            data: JSON.stringify(submitData),
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                window.location.href = '/system/' + data.systemUID + '/measurements';
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

    /*
     * Build select boxes dynamically, so we can allow multiple e.g. fish and plant
     * inputs in the input form
     */
    aqx_editsystem.make_select = function(selector, name, choices, initialEmpty) {
        var s = $('<select>').attr('name', name).addClass('form-control');
        if (initialEmpty) s.append($('<option>').attr('value', 0).text(""));
        $.each(choices, function (i, e) {
            s.append($('<option>').attr('value', e.id).text(e.name));
        });
        $(selector).replaceWith(s);
    };

    function makeInputRow(divID, typeName, num, choices, placeholder) {
        var selectID = 'select_' + typeName + '_' + num;
        var input = $('<input type="number" min="0" />')
            .addClass('form-control')
            .attr('name', typeName + 'Count_' + num)
            .attr('placeholder', placeholder);
        var newrow = $('<div>').addClass('form-group')
            .append($('<div>').addClass('row')
                    .append($('<div>').addClass('col-xs-8')
                            .append($('<div id="' + selectID + '">'))
                            .add($('<div>')
                                 .addClass('col-xs-4')
                                 .append(input))));
        $('#' + divID).replaceWith(newrow.add('<div id="' + divID + '"></div>'));
        aqx_editsystem.make_select('#' + selectID, typeName + 'ID_' + num, choices, true);
    }

    var numCropLists = 1;
    var numOrganismLists = 1;
    var MAX_LIST_LEN = 3;

    $(document).ready(function() {
        $('#get_geocoords').click(function () {
            address_to_geocode($("input[name='address']").val());
        });
        $('#create_form').submit(aqx_editsystem.create);
        $('#addcrop').click(function () {
            if (numCropLists <= MAX_LIST_LEN) {
                makeInputRow('newcrop', 'crop', numCropLists++, crops,
                             'Number of Crops');
                if (numCropLists == MAX_LIST_LEN) {
                    $('#addcrop').remove();
                }
            }
        });
        $('#addorganism').click(function () {
            if (numOrganismLists <= MAX_LIST_LEN) {
                makeInputRow('neworganism', 'organism', numOrganismLists++, organisms,
                             'Number of Organisms');
                if (numOrganismLists == MAX_LIST_LEN) {
                    $('#addorganism').remove();
                }
            }
        });
    });

}());
