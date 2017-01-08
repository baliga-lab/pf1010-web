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

    // These are in aqxGraph.js but not in aqxSystemGraph.js ...
    //aqxgraph.OVERLAY = true;
    aqxgraph.PRE_ESTABLISHED = 100;
    aqxgraph.ESTABLISHED = 200;
    // ---------------------

    aqxgraph.drawChart = function(getDataPointsForPlotHC) {
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
            callAPIForNewData(measurementIDList, aqxgraph.PRE_ESTABLISHED);
		    callAPIForNewData(measurementIDList, aqxgraph.ESTABLISHED);
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
    }

    aqxgraph.getAlertHTMLString = function(alertText, type) {
        return '<div class="alert alert-' + type + '"><a class="close" data-dismiss="alert">×</a><span>' +alertText + '</span></div>';
    }

    aqxgraph.getDataPoints = function(systemName, dataPoints, graphType, id, linkedTo,
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

    aqxgraph.createYAxis = function(yType, color, opposite, units) {
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

    aqxgraph.tooltipFormatter = function() {
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

}());
