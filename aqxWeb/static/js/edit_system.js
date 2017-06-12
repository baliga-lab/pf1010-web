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

    function convertFormData(data) {
        var submitData = { 'location': {}, 'gbMedia': [{'ID': 0}],
                           'crops': [],
                           'organisms': []
                         };
        // Translate into JSON for the backend API
        for (var i = 0; i < data.length; i++) {
            var obj = data[i];
            if (obj.name == 'name') submitData['name'] = obj.value;
            if (obj.name == 'startDate') submitData['startDate'] = obj.value;
            if (obj.name == 'location.lat') submitData['location']['lat'] = parseFloat(obj.value);
            if (obj.name == 'location.lng') submitData['location']['lng'] = parseFloat(obj.value);
            if (obj.name == 'techniqueID') submitData['techniqueID'] = parseInt(obj.value);
            if (obj.name == 'gbMediaID') submitData['gbMedia'][0]['ID'] = parseInt(obj.value);
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
        return submitData;
    }

    aqx_editsystem.update = function(url) {
        var data = $('#edit_form').serializeArray();
        var submitData = convertFormData(data);
        // This is a little tricky: JSON.stringify returns a string with double
        // quotes. If we use value with double quotes, the first double quote
        // will close the string in value, which does not result in what we want,
        // therefore, value uses single quotes
        var form = $('<form action="' + url + '" method="POST">' +
          '<input type="hidden" name="data" value=\'' + JSON.stringify(submitData) + '\'>' +
                     '</form>');
        // Another workaround for newer versions of Chrome: Form submission only
        // succeeds if the form is part of the body, otherwise an error is thrown
        // that the form is not connected
        $(document.body).append(form);
        form.submit();
        return false;
    };

    aqx_editsystem.create = function() {
        var data = $('#create_form').serializeArray();
        var submitData = convertFormData(data);
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
    aqx_editsystem.makeSelect = function(selector, name, choices, initialEmpty, selectedId) {
        var s = $('<select>').attr('name', name).addClass('form-control');
        if (initialEmpty) s.append($('<option>').attr('value', 0).text(""));
        $.each(choices, function (i, e) {
            var option = $('<option>').attr('value', e.id).text(e.name);
            if (e.id == selectedId) option.attr('selected', 'selected');
            s.append(option);
        });
        $(selector).replaceWith(s);
    };

    aqx_editsystem.makeDisplay = function(selector, name, choices, selectedId) {
        var s = '<input name="' + name + '" type="hidden" value="' + selectedId + '"></input>';
        var i;
        for (i = 0; i < choices.length; i++) {
            if (choices[i].id == selectedId) {
                s += '<input value="' + choices[i].name + '" class="form-control" readonly></input>';
                break;
            }
        }
        $(selector).replaceWith(s);
    }

    aqx_editsystem.makeInputRow = function(divID, typeName, num, choices, placeholder, selectedId, count,
                                           existing) {
        var selectID = 'select_' + typeName + '_' + num;
        var input = $('<input type="number" min="0" />')
            .addClass('form-control')
            .attr('name', typeName + 'Count_' + num)
            .attr('placeholder', placeholder);
        if (count) input.val(count);
        var formGroup = $('<div>').addClass('form-group');
        var newrow = $('<div>').addClass('row');
        var selectControl = $('<div>').addClass('col-xs-8').append($('<div id="' + selectID + '">'));
        var inputControl = existing ? $('<div>').addClass('col-xs-2').append(input)
            : $('<div>').addClass('col-xs-4').append(input);
        var removeControl = $('<div>').addClass('col-xs-2')
            .append($('<a>').addClass('form-control btn btn-default')
                    .attr('placeholder', '.col-xs-2')
                    .text('Remove'));

        newrow = newrow.append(selectControl);
        newrow = newrow.append(inputControl);

        if (existing) {
            if (existing) newrow = newrow.append(removeControl);
            formGroup = formGroup.append(newrow).add('<div id="' + divID + '"></div>');
            $('#' + divID).replaceWith(formGroup);
           // add that new HTML for the edit row to the DOM
            aqx_editsystem.makeDisplay('#' + selectID, typeName + 'ID_' + num, choices, selectedId);
        } else {
            // add that new HTML for the edit row to the DOM, but also add another
            // placeholder row to add more rows
            formGroup = formGroup.append(newrow).add('<div id="' + divID + '"></div>');
            $('#' + divID).replaceWith(formGroup);
            aqx_editsystem.makeSelect('#' + selectID, typeName + 'ID_' + num, choices, num > 0, selectedId);
        }
    };

    var numCropLists = 1;
    var numOrganismLists = 1;
    var MAX_LIST_LEN = 3;

    $(document).ready(function() {
        $('#get_geocoords').click(function () {
            address_to_geocode($("input[name='address']").val());
        });
        $('#addcrop').click(function () {
            if (numCropLists <= MAX_LIST_LEN) {
                aqx_editsystem.makeInputRow('newcrop', 'crop', numCropLists++, crops,
                                            'Number of Crops', false);
                if (numCropLists == MAX_LIST_LEN) {
                    $('#addcrop').remove();
                }
            }
        });
        $('#addorganism').click(function () {
            if (numOrganismLists <= MAX_LIST_LEN) {
                aqx_editsystem.makeInputRow('neworganism', 'organism', numOrganismLists++, organisms,
                                            'Number of Organisms', false);
                if (numOrganismLists == MAX_LIST_LEN) {
                    $('#addorganism').remove();
                }
            }
        });
    });

}());
