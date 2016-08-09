var Annotations = {
    bindDOMEvents: function () {
    $(window).load(function () {
     $('#otherType3').hide();
     $('#otherType1').hide();
     $('#otherType2').hide();
     $('#otherType4').hide();
     $('#otherType5').hide();
     $('#harvestPlantInfo').hide();
     $('#harvestFishInfo').hide();
     $('#phHighInfo').hide();
     $('#phLowInfo').hide();
     $('#fishAddInfo').hide();
     $('#fishRemoveInfo').hide();
     $('#bacteriaAddInfo').hide();
     $('#cleanTankYesInfo').hide();
     $('#plantAddInfo').hide();
     $('#plantRemoveInfo').hide();
     $('#reproductionYesInfo').hide();

     $('#number').hide();
 });



        $('#mySelect').change(function () {
            var selection1 = $(this).val();
            switch (selection1) {
                case 'fish':
                    $("#changeAdd").text("Fish Added");
                    $("#changeRemove").text("Fish Removed");
                    $('#otherType1').show();
                    var allRadios = document.getElementsByName('seg5');
                    var x = 0;
                    for (x = 0; x < allRadios.length; x++) {
                        if (allRadios[x].checked) {
                            allRadios[x].checked = false;
                        }
                    }
                    $('#number').val('');
                    $('#otherType2').hide();
                    $('#otherType3').hide();
                    $('#otherType4').hide();
                    $('#otherType5').hide();
                    $('#harvestPlantInfo').hide();
                    $('#harvestFishInfo').hide();
                    $('#phHighInfo').hide();
                    $('#phLowInfo').hide();
                    $('#bacteriaAddInfo').hide();
                    $('#cleanTankYesInfo').hide();
                    $('#plantAddInfo').hide();
                    $('#plantRemoveInfo').hide();
                    $('#reproductionYesInfo').hide();

                    break;

                case 'bacteria':
                    $("#changeJustAdd").text("Bacteria Added");
                    $('#otherType5').show();

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
                    $('#otherType1').hide();
                    $('#otherType4').hide();
                    $('#harvestPlantInfo').hide();
                    $('#harvestFishInfo').hide();
                    $('#phHighInfo').hide();
                    $('#phLowInfo').hide();
                    $('#fishAddInfo').hide();
                    $('#fishRemoveInfo').hide();
                    $('#plantAddInfo').hide();
                    $('#plantRemoveInfo').hide();
                    $('#reproductionYesInfo').hide();
                    $('#cleanTankYesInfo').hide();
                    break;

                case 'plant':
                    $("#changeAdd").text("Plant Added");
                    $("#changeRemove").text("Plant Removed");

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
                    $('#otherType4').hide();
                    $('#otherType5').hide();
                    $('#harvestPlantInfo').hide();
                    $('#harvestFishInfo').hide();
                    $('#phHighInfo').hide();
                    $('#phLowInfo').hide();
                    $('#bacteriaAddInfo').hide();
                    $('#cleanTankYesInfo').hide();
                    $('#fishAddInfo').hide();
                    $('#fishRemoveInfo').hide();
                    $('#reproductionYesInfo').hide();
                    break;
                case 'harvest':
                    $('#otherType4').show();

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
                    $('#otherType3').hide();
                    $('#otherType5').hide();
                    $('#phHighInfo').hide();
                    $('#phLowInfo').hide();
                    $('#fishAddInfo').hide();
                    $('#fishRemoveInfo').hide();
                    $('#bacteriaAddInfo').hide();
                    $('#cleanTankYesInfo').hide();
                    $('#plantAddInfo').hide();
                    $('#plantRemoveInfo').hide();
                    $('#reproductionYesInfo').hide();
                    break;
                case 'cleantank':
                    $("#changeYes").text("Clean Tank");
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
                    $('#otherType4').hide();
                    $('#otherType5').hide();
                    $('#harvestPlantInfo').hide();
                    $('#harvestFishInfo').hide();
                    $('#phHighInfo').hide();
                    $('#phLowInfo').hide();
                    $('#fishAddInfo').hide();
                    $('#fishRemoveInfo').hide();
                    $('#bacteriaAddInfo').hide();
                    $('#plantAddInfo').hide();
                    $('#plantRemoveInfo').hide();
                    $('#reproductionYesInfo').hide();
                    break;
                case 'reproduction':
                    $("#changeYes").text("Yes");
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
                    $('#otherType4').hide();
                    $('#otherType5').hide();
                    $('#harvestPlantInfo').hide();
                    $('#harvestFishInfo').hide();
                    $('#phHighInfo').hide();
                    $('#phLowInfo').hide();
                    $('#fishAddInfo').hide();
                    $('#fishRemoveInfo').hide();
                    $('#bacteriaAddInfo').hide();
                    $('#cleanTankYesInfo').hide();
                    $('#plantAddInfo').hide();
                    $('#plantRemoveInfo').hide();
                    break;
                case 'ph':
                    $('#otherType2').show();

                    $('#number').val('');

                    $('#otherType1').hide();
                    $('#otherType3').hide();
                    $('#otherType4').hide();
                    $('#otherType5').hide();
                    $('#harvestPlantInfo').hide();
                    $('#harvestFishInfo').hide();
                    $('#fishAddInfo').hide();
                    $('#fishRemoveInfo').hide();
                    $('#bacteriaAddInfo').hide();
                    $('#cleanTankYesInfo').hide();
                    $('#plantAddInfo').hide();
                    $('#plantRemoveInfo').hide();
                    $('#reproductionYesInfo').hide();
                    break;
                default:
                    $('#otherType1').hide();
                    $('#otherType2').hide();
                    $('#otherType3').hide();
                    $('#otherType4').hide();
                    $('#otherType5').hide();
                    $('#harvestPlantInfo').hide();
                    $('#harvestFishInfo').hide();
                    $('#phHighInfo').hide();
                    $('#phLowInfo').hide();
                    $('#fishAddInfo').hide();
                    $('#fishRemoveInfo').hide();
                    $('#bacteriaAddInfo').hide();
                    $('#cleanTankYesInfo').hide();
                    $('#plantAddInfo').hide();
                    $('#plantRemoveInfo').hide();
                    $('#reproductionYesInfo').hide();
                    $('#number').val('');
                    break;
            }
            var selection1 = $(this).val();
            var selection2 = $('#myForm').find('input:radio:checked').val();
            if (selection1 === "fish") {
                if (selection2 === "Remove") {
                    $('#fishRemoveInfo').show();
                    $('#fishAddInfo').hide();
                    $('#number').val('9');
                } else if (selection2 === "Add") {
                    $('#fishRemoveInfo').hide();
                    $('#fishAddInfo').show();
                    $('#number').val('8');
                }
            } else if (selection1 === "harvest") {
                if (selection2 === "harvestPlant") {
                    $('#harvestPlantInfo').show();
                    $('#harvestFishInfo').hide();
                    $('#number').val('4');
                } else if (selection2 === "harvestFish") {
                    $('#harvestFishInfo').show();
                    $('#harvestPlantInfo').hide();
                    $('#number').val('5');
                }
            } else if (selection1 === "ph") {
                if (selection2 === "High") {
                    $('#phHighInfo').show();
                    $('#phLowInfo').hide();
                    $('#number').val('3');
                } else if (selection2 === "Low") {
                    $('#phHighInfo').hide();
                    $('#phLowInfo').show();
                    $('#number').val('2');
                }
            } else if (selection1 === "plant") {
                if (selection2 === "Add") {
                    $('#plantRemoveInfo').hide();
                    $('#plantAddInfo').show();
                    $('#number').val('6');
                } else if (selection2 === "Remove") {
                    $('#plantRemoveInfo').show();
                    $('#plantAddInfo').hide();
                    $('#number').val('7');
                }
            } else if (selection1 === "bacteria") {
                if (selection2 === "justAdd") {
                    $('#bacteriaAddInfo').show();
                    $('#number').val('10');
                }
            } else if (selection1 === "cleantank") {
                if (selection2 === "Yes") {
                    $('#cleanTankYesInfo').show();
                    $('#number').val('12');
                }
            } else if (selection1 === "reproduction") {
                if (selection2 === "Yes") {
                    $('#reproductionYesInfo').show();
                    $('#number').val('14');
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
                    $('#fishRemoveInfo').show();
                    $('#fishAddInfo').hide();
                    $('#number').val('9');
                } else if (selection2 === "Add") {
                    $('#fishRemoveInfo').hide();
                    $('#fishAddInfo').show();
                    $('#number').val('8');
                }
            } else if (selection1 === "harvest") {
                if (selection2 === "harvestPlant") {
                    $('#harvestPlantInfo').show();
                    $('#harvestFishInfo').hide();
                    $('#number').val('4');
                } else if (selection2 === "harvestFish") {
                    $('#harvestFishInfo').show();
                    $('#harvestPlantInfo').hide();
                    $('#number').val('5');
                }
            } else if (selection1 === "ph") {
                if (selection2 === "High") {
                    $('#phHighInfo').show();
                    $('#phLowInfo').hide();
                    $('#number').val('3');
                } else if (selection2 === "Low") {
                    $('#phHighInfo').hide();
                    $('#phLowInfo').show();
                    $('#number').val('2');
                }
            } else if (selection1 === "plant") {
                if (selection2 === "Add") {
                    $('#plantRemoveInfo').hide();
                    $('#plantAddInfo').show();
                    $('#number').val('6');
                } else if (selection2 === "Remove") {
                    $('#plantRemoveInfo').show();
                    $('#plantAddInfo').hide();
                    $('#number').val('7');
                }
            } else if (selection1 === "bacteria") {
                if (selection2 === "justAdd") {
                    $('#bacteriaAddInfo').show();
                    $('#number').val('10');
                }
            } else if (selection1 === "cleantank") {
                if (selection2 === "Yes") {
                    $('#cleanTankYesInfo').show();
                    $('#number').val('12');
                }
            } else if (selection1 === "reproduction") {
                if (selection2 === "Yes") {
                    $('#reproductionYesInfo').show();
                    $('#number').val('14');
                }
            } else {
                $('#number').val('');
            }

        });
}
}

Annotations.bindDOMEvents();
var app = angular.module('aqx');

app.controller('AnnotationController', function ($scope, $http) {

    $scope.dataSubmit = function () {
        if ($('#recordedDateAndTime').val() != '' && $('#number').val() != '') {
            var systemID = $("#ID").html();
            var annotation = {annotationID: $('#number').val(), timestamp: $('#recordedDateAndTime').val()};
            $http.post('/aqxapi/v2/system/' + systemID + '/annotation', annotation).then(onSuccess, onFailure);
            function onSuccess(response) {
                console.log(response);
                alert("Recordings submitted sucessfully");
                window.location.reload();
            }

            function onFailure(error) {
                console.log(error);
                alert("Invalid data");
                window.location.reload();
            }
        } else {
            alert("Invalid data");
        }
    }


});