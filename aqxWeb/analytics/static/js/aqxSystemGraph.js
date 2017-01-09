"use strict";

var aqxgraph;
if (!aqxgraph) {
    aqxgraph = {};
}

(function () {

    aqxgraph.main = function() {

        // Select the default y-axis value
        aqxgraph.setDefaultYAxis();

        $("#selectStatus option[text='pre-established']").attr("selected","selected");

        // When the submit button is clicked, redraw the graph based on user selections
        $('#submitbtn').on('click', function() {
            $('#alert_placeholder').empty();
            aqxgraph.drawChart();
        });

        // Reset button, returns dropdowns to default, clears checklist, and displays default nitrate vs time graph
        $('#resetbtn').on('click', function(){

            // Reset X Axis selection to default
            $('#selectXAxis option').prop(aqxgraph.SELECTED, function() {
                return this.defaultSelected;
            });

            // Reset Graph Type selection to default
            $('#selectGraphType option').prop(aqxgraph.SELECTED, function() {
                return this.defaultSelected;
            });

            $('#' + aqxgraph.NUMBER_OF_ENTRIES + ' option').prop(aqxgraph.SELECTED, function() {
                return this.defaultSelected;
            });
            $('#alert_placeholder').empty();
            $('#analyzeContainer').show();

            // Select the default y-axis value
            aqxgraph.setDefaultYAxis();
            aqxgraph.drawChart();
        });

        $('#selectYAxis').bind("chosen:maxselected", function () {
            $('#alert_placeholder').html(aqxgraph.getAlertHTMLString("You can select up to " + aqxgraph.MAXSELECTIONS + " systems", 'danger'));
        });
    };

    window.onload = aqxgraph.onload;
}());
