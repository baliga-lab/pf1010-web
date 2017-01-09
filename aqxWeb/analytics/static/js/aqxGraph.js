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

    window.onload = function() {

        aqxgraph.HC_OPTIONS = {
            chart: {
                renderTo: 'analyzeContainer',
                type: 'line',
                zoomType: 'xy',
                backgroundColor: aqxgraph.BACKGROUND,
                plotBorderColor: '#606063'
            },
            title: {
                text: aqxgraph.CHART_TITLE,
                style: {
                    color: '#E0E0E3'
                }
            },
            credits: {
                style: {
                    color: '#666'
                }
            },
            tooltip: {
                formatter: aqxgraph.tooltipFormatter,
                crosshairs: [true,true]
            },
            legend: {
                itemStyle: {
                    color: '#E0E0E3'
                },
                enabled: true,
                labelFormatter: function() {
                    return '<span>'+ this.name.split(",")[0] + '</span>';
                },
                symbolWidth: 60
            },
            xAxis: {
                minPadding: 0.05,
                maxPadding: 0.05,
                title:
                {
                    text: aqxgraph.XAXIS_TITLE,
                    style: {color: 'white   '}
                }
            },
            exporting: {
                csv: {
                    columnHeaderFormatter: function(series) {
                        var name_and_variable = series.name.split(",");
                        return name_and_variable[0] + '-' + name_and_variable[1];
                    }
                }
            },
            showInLegend: true,
            series: []
        };
        try {
            aqxgraph.CHART = new Highcharts.Chart(aqxgraph.HC_OPTIONS);
        } catch(err) {
            console.log("Unable to initialize Highcharts Chart object!");
            console.log(err.stack);
        }
        Highcharts.setOptions(Highcharts.theme);
        // Render chart based on default page setting. i.e. x-axis & graph-type dropdowns, and the y-axis checklist
        aqxgraph.drawChart();
    };
}());
