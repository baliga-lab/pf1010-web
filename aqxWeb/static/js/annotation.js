$(window).load(function () {
    $('#otherType3').hide();
    $('#otherType1').hide();
    $('#otherType2').hide();
    $('#number').hide();

});


$('#mySelect').change(function () {
    var selection1 = $(this).val();
    switch (selection1) {
        case 'fish':
            $('#otherType1').show();
            var allRadios = document.getElementsByName('seg1');
            var x = 0;
            for (x = 0; x < allRadios.length; x++) {
                if (allRadios[x].checked) {
                    allRadios[x].checked = false;
                }
            }
            $('#number').val('');

            $('#otherType2').hide();
            $('#otherType3').hide();
            break;
        case 'bacteria':
            $('#otherType1').show();

            var allRadios = document.getElementsByName('seg1');
            var x = 0;
            for (x = 0; x < allRadios.length; x++) {
                if (allRadios[x].checked) {
                    allRadios[x].checked = false;
                }
            }
            $('#number').val('');

            $('#otherType2').hide();
            $('#otherType3').hide();
            break;

        case 'plant':
            $('#otherType1').show();

            var allRadios = document.getElementsByName('seg1');
            var x = 0;
            for (x = 0; x < allRadios.length; x++) {
                if (allRadios[x].checked) {
                    allRadios[x].checked = false;
                }
            }
            $('#number').val('');

            $('#otherType2').hide();
            $('#otherType3').hide();
            break;
        case 'harvest':
            $('#otherType3').show();

            var allRadios = document.getElementsByName('seg3');
            var x = 0;
            for (x = 0; x < allRadios.length; x++) {
                if (allRadios[x].checked) {
                    allRadios[x].checked = false;
                }
            }
            $('#number').val('');

            $('#otherType1').hide();
            $('#otherType2').hide();
            break;
        case 'cleartank':
            $('#otherType3').show();

            var allRadios = document.getElementsByName('seg3');
            var x = 0;
            for (x = 0; x < allRadios.length; x++) {
                if (allRadios[x].checked) {
                    allRadios[x].checked = false;
                }
            }
            $('#number').val('');

            $('#otherType1').hide();
            $('#otherType2').hide();
            break;
        case 'reproduction':
            $('#otherType3').show();

            var allRadios = document.getElementsByName('seg3');
            var x = 0;
            for (x = 0; x < allRadios.length; x++) {
                if (allRadios[x].checked) {
                    allRadios[x].checked = false;
                }
            }
            $('#number').val('');

            $('#otherType1').hide();
            $('#otherType2').hide();
            break;
        case 'Choose':
            $('#otherType3').hide();

            $('#number').val('');

            $('#otherType1').hide();
            $('#otherType2').hide();
            break;
        default:
            $('#otherType2').show();

            var allRadios = document.getElementsByName('seg2');
            var x = 0;
            for (x = 0; x < allRadios.length; x++) {
                if (allRadios[x].checked) {
                    allRadios[x].checked = false;
                }
            }
            $('#number').val('');

            $('#otherType1').hide();
            $('#otherType3').hide();
            break;
    }
    var selection1 = $(this).val();
    var selection2 = $('#myForm').find('input:radio:checked').val();
    if (selection1 === "fish") {
        if (selection2 === "Remove") {
            $('#number').val('9');
        } else if (selection2 === "Add") {
            $('#number').val('8');
        }
    } else if (selection1 === "harvest") {
        if (selection2 === "Yes") {
            $('#number').val('4');
        } else if (selection2 === "No") {
            $('#number').val('5');
        }
    } else if (selection1 === "ph") {
        if (selection2 === "Constant") {
            $('#number').val('1');
        } else if (selection2 === "High") {
            $('#number').val('2');
        } else if (selection2 === "Low") {
            $('#number').val('3');
        }
    } else if (selection1 === "plant") {
        if (selection2 === "Add") {
            $('#number').val('6');
        } else if (selection2 === "Remove") {
            $('#number').val('7');
        }
    } else if (selection1 === "bacteria") {
        if (selection2 === "Add") {
            $('#number').val('10');
        } else if (selection2 === "Remove") {
            $('#number').val('11');
        }
    } else if (selection1 === "cleartank") {
        if (selection2 === "Yes") {
            $('#number').val('12');
        } else if (selection2 === "No") {
            $('#number').val('13');
        }
    } else if (selection1 === "reproduction") {
        if (selection2 === "Yes") {
            $('#number').val('14');
        } else if (selection2 === "No") {
            $('#number').val('15');
        }
    } else {
        $('#number').val('');
    }
});

$('#myForm input').on('change', function () {
    var selection1 = $('#mySelect').val();
    var selection2 = $(this).val();
    if (selection1 === "fish") {
        if (selection2 === "Remove") {
            $('#number').val('9');
        } else if (selection2 === "Add") {
            $('#number').val('8');
        }
    } else if (selection1 === "harvest") {
        if (selection2 === "Yes") {
            $('#number').val('4');
        } else if (selection2 === "No") {
            $('#number').val('5');
        }
    } else if (selection1 === "ph") {
        if (selection2 === "Constant") {
            $('#number').val('1');
        } else if (selection2 === "High") {
            $('#number').val('2');
        } else if (selection2 === "Low") {
            $('#number').val('3');
        }
    } else if (selection1 === "plant") {
        if (selection2 === "Add") {
            $('#number').val('6');
        } else if (selection2 === "Remove") {
            $('#number').val('7');
        }
    } else if (selection1 === "bacteria") {
        if (selection2 === "Add") {
            $('#number').val('10');
        } else if (selection2 === "Remove") {
            $('#number').val('11');
        }
    } else if (selection1 === "cleartank") {
        if (selection2 === "Yes") {
            $('#number').val('12');
        } else if (selection2 === "No") {
            $('#number').val('13');
        }
    } else if (selection1 === "reproduction") {
        if (selection2 === "Yes") {
            $('#number').val('14');
        } else if (selection2 === "No") {
            $('#number').val('15');
        }
    } else {
        $('#number').val('');
    }

});


function dataSubmit() {
    alert("Id submitted:  " + $('#number').val());
}