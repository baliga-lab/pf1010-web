"use strict";

/*
  This is an intermediary step to remove the horrible redundancy in aqxSystemGraph.js
  and aqxGraph.js while retaining the functionality. Step-by-step we empty out the common
  parts and hopefully end up with a single javascript file for the analytics.
*/

var aqxgraph;
if (!aqxgraph) {
    aqxgraph = {};
}

(function () {
    /* ###############################################################################
       CONSTANTS
       ############################################################################### */

    aqxgraph.XAXIS = "selectXAxis";
    aqxgraph.XAXIS_TITLE = 'Hours since creation';
    aqxgraph.CHART = "";
    aqxgraph.GRAPH_TYPE = "selectGraphType";
    /*
      Used to display data that was entered by user in the past
      "" - Used to display all the data that user has recorded
      30 - Displays all the data recorded in the past 30 days
      60 - Displays all the data recorded in the past 60 days
      90 - Displays all the data recorded in the past 90 days
    */
    aqxgraph.NUM_ENTRIES_ELEMENT_ID = 'selectNumberOfEntries';
    aqxgraph.SELECTED = 'selected';
    aqxgraph.DEFAULT_Y_TEXT = "Nitrate";
    aqxgraph.DEFAULT_Y_VALUE = aqxgraph.DEFAULT_Y_TEXT.toLowerCase();
    aqxgraph.CHART_TITLE = "System Analyzer";
    aqxgraph.HC_OPTIONS;
    aqxgraph.COLORS = ["lime", "orange", '#f7262f', "lightblue"];
    aqxgraph.DASHSTYLES = ['Solid', 'LongDash', 'ShortDashDot', 'ShortDot', 'LongDashDotDot'];
    aqxgraph.MARKERTYPES = ["circle", "square", "diamond", "triangle", "triangle-down"];
    aqxgraph.DANGER = 'danger';
    aqxgraph.MAXSELECTIONS = 4;
    aqxgraph.BACKGROUND = {
        linearGradient: { x1: 0, y1: 0, x2: 1, y2: 1 },
        stops: [ [0, '#2a2a2b'], [1, '#3e3e40'] ]
    };
    var PRE_ESTABLISHED = 100;
    var ESTABLISHED = 200;

    aqxgraph.drawChart = function() {
        var graphType = document.getElementById(aqxgraph.GRAPH_TYPE).value;
        var status = document.getElementById("selectStatus").value;

        // Get measurement types to display on the y-axis
        var yTypes = $("#selectYAxis").val();
        var numberOfEntries = document.getElementById(aqxgraph.NUM_ENTRIES_ELEMENT_ID).value;

        // Generate a data Series for each system and y-value type, and assign them all to the CHART
        updateChartDataPointsHC(aqxgraph.CHART, yTypes, graphType, numberOfEntries, status,
                                getDataPointsForPlotHC).redraw();
    };

    function updateChartDataPointsHC(chart, yTypeList, graphType, numberOfEntries, status,
                                     getDataPointsForPlotHC) {

        chart = clearOldGraphValues(chart);

        // Determine if any measurements are not already tracked in systems_and_measurements
        var activeMeasurements = getAllActiveMeasurements();
        var measurementsToFetch = _.difference(yTypeList, activeMeasurements);

        // If there are any measurements to fetch, get the ids then pass those to the API
        // along with the system names
        // and add the new dataPoints to the systems_and_measurements object
        // Data is requested for both established and pre-established data, which is labeled as such
        if (measurementsToFetch.length > 0) {
            var measurementIDList = [];
            _.each(measurementsToFetch, function(measurement){
                measurementIDList.push(measurement_types_and_info[measurement].id);
            });
            callAPIForNewData(measurementIDList, PRE_ESTABLISHED);
		    callAPIForNewData(measurementIDList, ESTABLISHED);
        }
        chart.xAxis[0].setTitle({ text: aqxgraph.XAXIS_TITLE });
        var newDataSeries = getDataPointsForPlotHC(chart, yTypeList, graphType, numberOfEntries, status);
        _.each(newDataSeries, function(series) {
            chart.addSeries(series);
        });
        return chart;
    }

    function clearOldGraphValues(chart) {
        // Clear yAxis
        while(chart.yAxis.length > 0) {
            chart.yAxis[0].remove(true);
        }
        // Clear series data
        while (chart.series.length > 0) {
            chart.series[0].remove(true);
        }
        return chart;
    }

    function getAllActiveMeasurements() {
        // Grab all measurement types in the checklist
        var activeMeasurements = [];
        var systemMeasurements = _.first(systems_and_measurements).measurement;
        _.each(systemMeasurements, function(measurement) {
            activeMeasurements.push(measurement.type.toLowerCase());
        });
        return activeMeasurements;
    }

    function addNewMeasurementData(data, statusID){
        var systems = data.response;

        _.each(systems, function(system) {
            var systemMeasurements = system.measurement;
            _.each(systemMeasurements, function(measurement) {
                measurement.status = statusID.toString()
            });
            _.each(systems_and_measurements, function(existingSystem){
                // Match systems in the new data by id, and then add the new measurements
                // to the list of existing measurements
                if (_.isEqual(existingSystem.system_uid, system.system_uid)){
                    existingSystem.measurement = existingSystem.measurement.concat(systemMeasurements);
                }
            });
        });
    }

    function processAJAXResponse(data, status){
        if("error" in data){
            console.log(data);
            throw "AJAX request reached the server but returned an error!";
        } else {
            console.log("here");
            addNewMeasurementData(data, status);
        }
    }

    function callAPIForNewData(measurementIDList, statusID){
        $.ajax({
            type: 'POST',
            contentType: 'application/json;charset=UTF-8',
            dataType: 'json',
            async: false,
            url: '/dav/aqxapi/v1/measurements/plot',
            data: JSON.stringify({systems: selectedSystemIDs, measurements: measurementIDList, status: statusID}, null, '\t'),
            // Process API response
            success: function(data){
                processAJAXResponse(data, statusID)
            },
            // Report any AJAX errors
            error: ajaxError
        });
    }

    function ajaxError(jqXHR, textStatus, errorThrown){
        var redirectLink = 'error';
        alert('Unable to access the server... Look at the console (F12) for more information!');
        console.log('jqXHR:');
        console.log(jqXHR);
        console.log('textStatus:');
        console.log(textStatus);
        console.log('errorThrown:');
        console.log(errorThrown);
        window.location.href = redirectLink;
    }

    aqxgraph.setDefaultYAxis = function() {
        $("#selectYAxis").chosen({
            max_selected_options: aqxgraph.MAXSELECTIONS,
            no_results_text: "Oops, nothing found!",
            width: "100%"
        });
        $('#selectYAxis').val('');
        $('#selectYAxis option[value=' + aqxgraph.DEFAULT_Y_VALUE + ']').prop('selected', true);
        $('#selectYAxis').trigger("chosen:updated");
    };

    aqxgraph.getAlertHTMLString = function(alertText, type) {
        return '<div class="alert alert-' + type + '"><a class="close" data-dismiss="alert">×</a><span>' +alertText + '</span></div>';
    };

    function getDataPoints(systemName, dataPoints, graphType, id, linkedTo,
                           color, yAxis, dashStyle, markerType, yType) {
        var series = { name: systemName + ',' + yType,
                       type: graphType,
                       data: dataPoints,
                       color: color,
                       id: id,
                       yAxis: yAxis,
                       dashStyle: dashStyle,
                       turboThreshold:0,
                       marker: {symbol: markerType}
                     };
        if (linkedTo) {
            series.linkedTo = id;
        }
        return series;
    }

    function createYAxis(yType, color, opposite, units) {
        var unitLabel;
        if (units) {
            unitLabel = (_.isEqual(units, "celsius")) ? "°C" : units;
        } else {
            unitLabel = "";
        }
        return {
            title:
            {
                text: yType,
                style: {color: color}
            },
            labels:
            {
                format: '{value} ' + unitLabel,
                style: {color: color}
            },
            showEmpty: false,
            lineWidth: 1,
            tickWidth: 1,
            gridLineWidth: 1,
            opposite: opposite,
            gridLineColor: '#707073',
            lineColor: '#707073',
            minorGridLineColor: '#505053',
            tickColor: '#707073'
        };
    }

    function tooltipFormatter() {
        var tooltipInfo = this.series.name.split(",");
        var yVal = tooltipInfo[1];
        var units = measurement_types_and_info[yVal].unit;
        units = (units) ? units : "";
        units = (_.isEqual(units, "celsius")) ? "°C" : units;
        yVal = yVal.charAt(0).toUpperCase() + yVal.slice(1);
        var datetime = this.point.date.split(" ");
        var eventString = "";
        if (this.point.annotations) {
            eventString = "<br><p>Most recent event(s): </p>";
            _.each(this.point.annotations, function (event) {
                eventString = eventString + '<br><p>' + annotationsMap[event.id]+ " at " + event.date + '<p>'
            });
        }
        return '<b>' + tooltipInfo[0] + '</b>' +
            '<br><p>' + yVal + ": " + this.y + ' ' + units + '</p>' +
            '<br><p>Hours in cycle: ' + this.x + '</p>' +
            '<br><p>Measured on: ' + datetime[0] + '</p>' +
            '<br><p>At time: ' + datetime[1] +'</p>' +
            eventString;
    }

    function copyYAxes(yAxes){
        var axesToAdd = [];
        _.each(yAxes, function(axis){
            var axisLabel = axis.userOptions.title.text;
            axesToAdd.push(createYAxis(axisLabel,
                                       axis.userOptions.title.style.color,
                                       axis.opposite));
        });
        return axesToAdd;
    }

    function copySeries(series, systemID){
        var seriesToAdd = [];
        _.each(series, function (seriesItem) {
            if(_.isEqual(seriesItem.userOptions.id, systemID)){
                var linkedTo = false;
                if (seriesItem.userOptions.linkedTo) linkedTo = true;
                seriesToAdd.push(getDataPoints(
                    seriesItem.name,
                    seriesItem.userOptions.data,
                    seriesItem.userOptions.type,
                    seriesItem.userOptions.id,
                    linkedTo,
                    seriesItem.color,
                    seriesItem.userOptions.yAxis,
                    seriesItem.userOptions.dashStyle,
                    seriesItem.userOptions.marker.symbol,
                    ""
                ));
            }
        });
        return seriesToAdd;
    }

    aqxgraph.toggleSplitMode = function() {
        // Can only split with 2+ systems
        if (selectedSystemIDs.length > 1) {

            // List of new charts
            var splitCharts = [];

            // Grab series and yAxes from the overlay chart
            var yAxes = aqxgraph.CHART.yAxis;
            var series = aqxgraph.CHART.series;

            _.each(selectedSystemIDs, function(systemID, k) {
                // Copy over formatting options from overlay chart
                var new_opts = {
                    chart: {
                        type: 'line',
                        height: 200,
                        renderTo: 'chart-' + k,
                        zoomType: 'xy',
                        backgroundColor: aqxgraph.BACKGROUND,
                        plotBorderColor: '#606063'
                    },
                    title: {
                        text: "NO DATA FOR THIS SYSTEM",
                        style: { color: '#E0E0E3' }
                    },
                    credits: { style: { color: '#666' } },
                    tooltip: {
                        formatter: tooltipFormatter,
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
                            style: {color: 'white'}
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
                    yAxis: copyYAxes(yAxes),
                    series: copySeries(series, systemID)
                };

                // Loop through series to extract system names and assign as titles. If there is no data
                // for a system, then the series will not exist and the name remains "NO DATA FOR THIS SYSTEM"
                for (var i = 0; i < series.length; i++) {
                    if (_.isEqual(systemID, series[i].userOptions.id)) {
                        new_opts.title.text = series[i].name.split(",")[0].trim();
                    }
                }

                // Add new split chart to list of charts
                var chart = new Highcharts.Chart(new_opts);
                splitCharts.push(chart);
            });

            // Draw the split charts
            _.each(splitCharts, function(chart) { chart.redraw(); });
        }
    };

    // Axis dict ensures that each variable is plotted to the same, unique axis for that variable
    // i.e. nitrate values for each system to axis 0, pH values for each system to axis 1, etc.
    // e.g.
    // {
    //   'nitrate' : {isAxis : true, axis : 0},
    //   'pH' : {isAxis : false},
    //   'o2' : {isAxis : true, axis : 1}
    // }
    function initAxes(yTypeList) {
        var axes = {};
        _.each(yTypeList, function(axis) {
            axes[axis] = {isAxis:false};
        });
        return axes;
    }

    function displayMissingYTypesAlert(missingYTypes) {
        if (missingYTypes.length > 0) {
            var alertString = '<div>Missing values for: </div>';
            alertString += '<ul>';
            for (var i = 0; i < missingYTypes.length; i++) {
                var entry = missingYTypes[i];
                alertString += '<li>' + entry.system + ": " + entry.ytype + '</li>';
            }
            alertString += '</ul>';
            $('#alert_placeholder').html(aqxgraph.getAlertHTMLString(alertString, aqxgraph.DANGER));
        }
    }

    function getDataPointsForPlotHC(chart, yTypeList, graphType, numberOfEntries, status) {

        var dataPointsList = [];
        var missingYTypes = [];
        var numAxes = 0;
        var axes = initAxes(yTypeList);

        _.each(systems_and_measurements, function(system, j) {

            var measurements = system.measurement;
            // Used to group measurement types by system, by linking them to an id. This ensures that the legend only
            // shows "SystemName", instead of "SystemName-nitrate" "SystemName-pH", etc.
            var linkedTo = false;

            _.each(yTypeList, function(yType) {
                var numValues = 0;
                _.each(measurements, function(measurement) {
                    if (measurement.type.toLowerCase() == yType.toLowerCase() &&
                        (status == '0' || measurement.status == status)) {
                        var systemId = system.system_uid;

                        // Check if there is data for this system and measurement type
                        if (measurement.values.length > 0) {

                            // Has this variable been assigned an axis yet?
                            // If not, create the axis and assign to a variable. This variables isAxis is now true,
                            // an axis is assigned, and the numAxes increments
                            if (!axes[yType].isAxis) {
                                chart.addAxis(createYAxis(yType, aqxgraph.COLORS[numAxes],
                                                          numAxes % 2,
                                                          measurement_types_and_info[yType].unit));
                                axes[yType].isAxis = true;
                                axes[yType].axis = numAxes++;
                            }
                            // Number of the axis this series is plotted against, this determines line color and links
                            // a series to this axis
                            var yAxis = axes[yType].axis;

                            // IMPORTANT: MEASUREMENT VALUES should be sorted by date to display
                            var dataValues = measurement.values;

                            // Collect only the desired number of data points, this can be 30, 60, 90, or all data points.
                            if (!_.isEmpty(numberOfEntries)) {
                                dataValues = _.last(dataValues, numberOfEntries);
                            }

                            // Generate the Object containing data and configurations for this particular series and push to
                            // th list of series to plot
                            dataPointsList.push(getDataPoints(system.name, dataValues, graphType,
                                                              systemId, linkedTo,
                                                              aqxgraph.COLORS[yAxis], yAxis,
                                                              aqxgraph.DASHSTYLES[j],
                                                              aqxgraph.MARKERTYPES[j], yType));
                            linkedTo = true;
                            numValues++;
                        }
                    }
                });

                // If there is no data for the given system, measurement type, and status, we will warn the user
                // for this system and measurement type
                if (numValues == 0) {
                    missingYTypes.push({'system': system.name, 'ytype': yType})
                }
            });
        });

        displayMissingYTypesAlert(missingYTypes);
        return dataPointsList;
    }

    aqxgraph.onload = function() {

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
                formatter: tooltipFormatter,
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
