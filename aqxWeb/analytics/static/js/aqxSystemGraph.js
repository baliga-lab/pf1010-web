"use strict";

var aqxgraph;
if (!aqxgraph) {
    aqxgraph = {};
}

(function () {

    function getDataPointsForPlotHC(chart, yTypeList, graphType, numberOfEntries, status) {

        // DataPoints to add to chart
        var dataPointsList = [];

        // The name of a system and the y variable for which it is missing data
        var missingYTypes = [];

        // Track the number of axes being used
        var numAxes = 0;

        // Axis dict ensures that each variable is plotted to the same, unique axis for that variable
        // i.e. nitrate values for each system to axis 0, pH values for each system to axis 1, etc.
        var axes = {};
        _.each(yTypeList, function(axis) {
            axes[axis] = {isAxis:false};
        });

        // Begin iterating through the systems
        _.each(systems_and_measurements, function(system, j) {

            var measurements = system.measurement;
            // Used to link measurements to the same system
            var linkedTo = false;

            // Loop through selected measurement types
            _.each(yTypeList, function(yType) {

                // Then find matching types in the systems_and_measurements object
                _.each(measurements, function(measurement) {
                    if (_.isEqual(measurement.type.toLowerCase(), yType.toLowerCase()) &&
                        _.isEqual(measurement.status, status)) {
                        var systemId = system.system_uid;

                        // Check if there is data for this system and measurement type
                        if (measurement.values.length > 0) {

                            // Has this variable been assigned an axis yet?
                            // If not, create the axis and assign to a variable. This variables isAxis is now true,
                            // an axis is assigned, and the numAxes increments
                            if (!axes[yType].isAxis) {
                                chart.addAxis(aqxgraph.createYAxis(yType, aqxgraph.COLORS[numAxes], (numAxes % 2) , measurement_types_and_info[yType].unit));
                                axes[yType].isAxis = true;
                                axes[yType].axis = numAxes++;
                            }
                            var yAxis = axes[yType].axis;
                            // IMPORTANT: MEASUREMENT VALUES should be sorted by date to display
                            var dataValues = measurement.values;
                            if (!_.isEmpty(numberOfEntries)) {
                                dataValues = _.last(dataValues, numberOfEntries);
                            }
                            // Push valid dataPoints and their configs to the list of dataPoints to plot
                            dataPointsList.push(
                                aqxgraph.getDataPoints(system.name, dataValues, graphType,
                                                       systemId, linkedTo,
                                                       aqxgraph.COLORS[yAxis], yAxis,
                                                       aqxgraph.DASHSTYLES[j],
                                                       aqxgraph.MARKERTYPES[j], yType));
                            linkedTo = true;
                        }

                        // If there is no data, we will warn the user for this system and variable
                        else{
                            missingYTypes.push(system.name + "-" + yType);
                        }
                    }
                });
            });
        });

        // Warn the user about missing data
        if (missingYTypes.length > 0){
            $('#alert_placeholder').html(aqxgraph.getAlertHTMLString("Missing values for: " + missingYTypes.toString(), aqxgraph.DANGER));
        }
        return dataPointsList;
    }

    /**
     *  main - Sets behaviors for Submit and Reset buttons, populates y-axis dropdown, and checks nitrate as default y-axis
     */
    aqxgraph.main = function() {

        // Select the default y-axis value
        aqxgraph.setDefaultYAxis();

        $("#selectStatus option[text='pre-established']").attr("selected","selected");

        // When the submit button is clicked, redraw the graph based on user selections
        $('#submitbtn').on('click', function() {
            $('#alert_placeholder').empty();
            aqxgraph.drawChart(getDataPointsForPlotHC);
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
            aqxgraph.drawChart(getDataPointsForPlotHC);
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
                    columnHeaderFormatter: function(series){
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
        } catch(err){
            console.log("Unable to initialize Highcharts Chart object!");
            console.log(err.stack);
        }
        Highcharts.setOptions(Highcharts.theme);
        // Render chart based on default page setting. i.e. x-axis & graph-type dropdowns, and the y-axis checklist
        aqxgraph.drawChart(getDataPointsForPlotHC);
    };

}());
