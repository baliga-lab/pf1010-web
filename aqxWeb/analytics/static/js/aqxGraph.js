"use strict";

var aqxgraph;
if (!aqxgraph) {
    aqxgraph = {};
}

(function () {

    aqxgraph.main = function() {

        // Select the default y-axis value
        aqxgraph.setDefaultYAxis();

        // Setup overlay/split toggle
        $('.toggle').toggles({text:{on:'OVERLAY',off:'SPLIT'}, on:true});

        // Disable when graphing only one system
        if(_.isEqual(selectedSystemIDs.length, 1)) {
            $('.toggle').toggleClass('disabled', true);
        }

        // Hide split graphs and show overlay when active
        // When deactivated, create split graphs an hide overlay graph
        $('.toggle').on('toggle', function(e, active) {
            if (active) {
                $('[id^=chart-]').hide();
                $('#analyzeContainer').show();
            } else {
                $('[id^=chart-]').show();
                $('#analyzeContainer').hide();
                aqxgraph.toggleSplitMode();
            }
        });

        // When the submit button is clicked, redraw the graph based on user selections
        $('#submitbtn').on('click', function() {
            $('#alert_placeholder').empty();
            aqxgraph.drawChart();

            // Check if the toggle is active. (i.e, overlay mode enabled)
            // If in split mode, make the split graphs
            if (!$('.toggle').data('toggles').active) {
                aqxgraph.toggleSplitMode();
            }
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

            $('#selectStatus option').prop(aqxgraph.SELECTED, function() {
                return this.defaultSelected;
            });

            $('#' + aqxgraph.NUM_ENTRIES_ELEMENT_ID + ' option').prop(aqxgraph.SELECTED, function() {
                return this.defaultSelected;
            });

            $('#alert_placeholder').empty();

            $('[id^=chart-]').hide();
            $('#analyzeContainer').show();
            $('.toggle').data('toggles').toggle(true, false, true);

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
