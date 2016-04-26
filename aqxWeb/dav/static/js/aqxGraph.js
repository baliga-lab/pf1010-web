"use strict";
/* ##################################################################################################################
 CONSTANTS
 ################################################################################################################### */

var XAXIS = "selectXAxis";
var XAXIS_TITLE = 'Hours since creation';
var CHART = "";
var GRAPH_TYPE = "selectGraphType";
var NUM_ENTRIES_ELEMENT_ID = 'selectNumberOfEntries';
var SELECTED = 'selected';
var DEFAULT_Y_TEXT = "Nitrate";
var DEFAULT_Y_VALUE = DEFAULT_Y_TEXT.toLowerCase();
var CHART_TITLE = "System Analyzer";
var HC_OPTIONS;
var COLORS = ["lime", "orange", '#f7262f', "lightblue"];
var DASHSTYLES = ['Solid', 'LongDash', 'ShortDashDot', 'ShortDot', 'LongDashDotDot'];
var MARKERTYPES = ["circle", "square", "diamond", "triangle", "triangle-down"];
var DANGER = 'danger';
var MAXSELECTIONS = 4;
var BACKGROUND = {
    linearGradient: { x1: 0, y1: 0, x2: 1, y2: 1 },
    stops: [
        [0, '#2a2a2b'],
        [1, '#3e3e40']
    ]
};
var OVERLAY = true;
var PRE_ESTABLISHED = 100;
var ESTABLISHED = 200;
var SPACE = ' ';
var GMT = 'GMT';

/* ##################################################################################################################
 MAIN CHART LOADING FUNCTIONS
 #################################################################################################################### */

/**
 * Draws a graph given a graph type, x-axis values, y-axis values, system status, and desired number of data points
 * These values are all obtained from the dropdowns.
 */
function drawChart(){
    var graphType = document.getElementById(GRAPH_TYPE).value;
    var xType = document.getElementById(XAXIS).value;
    var status = document.getElementById("selectStatus").value;

    // Get measurement types to display on the y-axis
    var yTypes = $("#selectYAxis").val();
    var numberOfEntries = document.getElementById(NUM_ENTRIES_ELEMENT_ID).value;

    // Generate a data Series for each system and y-value type, and assign them all to the CHART
    updateChartDataPointsHC(CHART, xType, yTypes, graphType, numberOfEntries, status).redraw();
}


/**
 *
 * @param chart - A CanvasJS chart
 * @param xType - X-axis value chosen from dropdown
 * @param yTypeList - List of y-axis values selected from the checklist
 * @param graphType - The graph type chosen from dropdown
 * @param numberOfEntries - used to display data entered by user in the past
 * @oaram status - The selected system status, PRE_ESTABLISHED or ESTABLISHED
 *
 * Given a Chart, desired X and Y values, System Status, and Number of Data Points, determine
 * if this data is stored in the browser or needs to be retrieved from the Database using AJAX.
 * Any requisite data is loaded from the server into the stored list, and data Series are generated
 */
function updateChartDataPointsHC(chart, xType, yTypeList, graphType, numberOfEntries, status){

    // Clear the old chart's yAxis and dataPoints. This must be done manually.
    chart = clearOldGraphValues(chart);

    // Determine if any measurements are not already tracked in systems_and_measurements list
    var activeMeasurements = getAllActiveMeasurements();
    var measurementsToFetch = _.difference(yTypeList, activeMeasurements);

    // If there are any measurements to fetch, get the ids then pass those to the API along with the system names
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

    // Label the x axis, for now just using time on the x axis
    // TODO: Expand to handle changing x axes
    chart.xAxis[0].setTitle({ text: XAXIS_TITLE });

    // Generate a list of data series and their configuration options. Then add each object to the Chart options.
    var newDataSeries = getDataPointsForPlotHC(chart, xType, yTypeList, graphType, numberOfEntries, status);
    _.each(newDataSeries, function(series) {
        chart.addSeries(series);
    });

    return chart;
}


// TODO: This will need to be re-evaluated to incorporate non-time x-axis values. For now, stubbing xType for this.
/**
 *
 * @param chart - A Highcharts Chart to which data will be added
 * @param xType - X-axis values. Ex: Time, pH, Hardness
 * @param yTypeList - Y-axis values. Ex: [pH, Nitrate]
 * @param graphType - Type of graph to display. Ex: line, scatter
 * @param numberOfEntries - used to display data entered by user in the past
 * @returns {Array} - An array of dataPoints of yType measurement data for all systems
 *
 * Returns a list of data series for each system, measurement type, and status combination requested.
 * These series also contain configurations for color, dash style, graph type, and which axis the data
 * is plotted against.
 */
function getDataPointsForPlotHC (chart, xType, yTypeList, graphType, numberOfEntries, status){

    // DataPoints to add to chart
    var dataPointsList = [];

    // The name of a system and the y variable for which it is missing data. used to warn users
    // of which systems are missing requested data, and for which measurement.
    var missingYTypes = "";

    // Track the number of y axes being used.
    var numAxes = 0;

    // Axis dict ensures that each variable is plotted to the same, unique axis for that variable
    // i.e. nitrate values for each system to axis 0, pH values for each system to axis 1, etc.
    // e.g.
    // {
    //   'nitrate' : {isAxis : true, axis : 0},
    //   'pH' : {isAxis : false},
    //   'o2' : {isAxis : true, axis : 1}
    // }
    var axes = {};
    _.each(yTypeList, function(yType){
        axes[yType] = {isAxis:false};
    });

    // Begin iterating through the systems
    _.each(systems_and_measurements, function(system, j){

        var measurements = system.measurement;
        // Used to group measurement types by system, by linking them to an id. This ensures that the legend only
        // shows "SystemName", instead of "SystemName-nitrate" "SystemName-pH", etc.
        var linkedTo = false;

        // Loop through selected measurement types
        _.each(yTypeList, function(yType) {

            // Find the measurement data entry that matches the given YType and Status ID
            _.each(measurements, function(measurement){
                if (_.isEqual(measurement.type.toLowerCase(), yType.toLowerCase()) &&
                    _.isEqual(measurement.status, status)) {

                    var systemId = system.system_uid;

                    // Check if there is data for this system and measurement type
                    if (measurement.values.length > 0){

                        // Has this variable been assigned an axis yet?
                        // If not, create the axis and assign to a variable. This variables isAxis is now true,
                        // an axis is assigned, and the numAxes increments
                        if (!axes[yType].isAxis) {
                            chart.addAxis(createYAxis(yType, COLORS[numAxes], (numAxes % 2) , measurement_types_and_info[yType].unit));
                            axes[yType].isAxis = true;
                            axes[yType].axis = numAxes++;
                        }

                        // Number of the axis this series is plotted against, this determines line color and links
                        // a series to this axis
                        var yAxis = axes[yType].axis;

                        // IMPORTANT: MEASUREMENT VALUES should be sorted by date to display
                        var dataValues = measurement.values;

                        // Collect only the desired number of data points, this can be 30, 60, 90, or all data points.
                        if(!_.isEmpty(numberOfEntries)) {
                            dataValues = _.last(dataValues, numberOfEntries);
                        }

                        // Generate the Object containing data and configurations for this particular series and push to
                        // th list of series to plot
                        dataPointsList.push(
                            getDataPoints(system.name, dataValues, graphType, systemId, linkedTo, COLORS[yAxis], yAxis, DASHSTYLES[j], MARKERTYPES[j], yType));
                        linkedTo = true;
                    }

                    // If there is no data for the given system, measurement type, and status, we will warn the user
                    // orr this system and variable
                    else{
                        missingYTypes = missingYTypes +  "<li>"+ system.name + " - " + yType + "</li>";
                    }
                }
            });
        });
    });

    // Populate the alert message if necessary, and display it
    if (missingYTypes.length > 0){
        $('#alert_placeholder').html(getAlertHTMLString("These system(s) do not have any data for the selected period: " + missingYTypes, DANGER));
    }

    return dataPointsList;
}


/* ##################################################################################################################
 AJAX CALLS TO GRAB NEW DATA
 #################################################################################################################### */


/**
 * Take measurement data object from AJAX response, and add to the global systems_and_measurements data
 *
 * @param data - The JSON response from the server
 * @param statusID - The statusID parameter for which data was requested. This ID is used to label
 *                   the response on the frontend with its respective system status
 */
function addNewMeasurementData(data, statusID){
    console.log('success',data);
    var systems = data.response;

    // Loop through existing systems in the systems_and_measurements object
    _.each(systems, function(system){
        var systemMeasurements = system.measurement;
        _.each(systemMeasurements, function(measurement){
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


/**
 * Some custom error handling for the server response. If there is a non-AJAX related server error, log the
 * corresponding error response to the console. Otherwise, proceed and add the new data to the currently stored data
 *
 * @param data - The JSON response from the server
 * @param statusID - The statusID parameter for which data was requested. This ID is used to label
 *                   the response on the frontend with its respective system status
 *
 */

function processAJAXResponse(data, statusID){
    if("error" in data){
        console.log("Server returned an error...");
        console.log(data);
        throw "AJAX request reached the server but returned an error!";
    }else{
        addNewMeasurementData(data, statusID);
    }
}


/**
 * Sends an AJAX POST request to call for new, untracked measurement data for each system
 *
 * @param measurementIDList - List of measurement IDs for which data is being requested
 * @param statusID - System status ID for which data is being requested
 */
function callAPIForNewData(measurementIDList, statusID){
    $.ajax({
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        dataType: 'json',
        async: false,
        url: '/dav/aqxapi/v1/measurements/plot',
        data: JSON.stringify({systems: selectedSystemIDs, measurements: measurementIDList, status: statusID}, null, '\t'),
        // Process API response if AJAX succesfully accessed the server
        success: function(data){
            processAJAXResponse(data, statusID)
        },
        // Report any AJAX-related errors
        error: ajaxError
    });
}

// Report any and all AJAX-related errors to the console.
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


/* ##################################################################################################################
 HELPER FUNCTIONS
 #################################################################################################################### */


/**
 * Returns a list of all y-variables currently being stored
 * @returns {Array} - An array of all measurement types currently being stored
 */
function getAllActiveMeasurements() {
    // Grab all measurement types in the checklist
    var activeMeasurements = [];
    var systemMeasurements = _.first(systems_and_measurements).measurement;
    _.each(systemMeasurements, function(measurement){
        activeMeasurements.push(measurement.type.toLowerCase());
    });
    return activeMeasurements;
}


/**
 * Removes any data series' and y-axes from the given chart
 * @param chart
 * @returns {*}
 */
function clearOldGraphValues(chart) {
    // Clear yAxis
    while(chart.yAxis.length > 0){
        chart.yAxis[0].remove(true);
    }
    // Clear series data
    while(chart.series.length > 0) {
        chart.series[0].remove(true);
    }
    return chart;
}


/**
 *
 * Returns the Y Axis text selector to default
 */
function setDefaultYAxis() {
    $("#selectYAxis").chosen({
        max_selected_options: MAXSELECTIONS,
        no_results_text: "Oops, nothing found!",
        width: "100%"
    });
    $('#selectYAxis').val('');
    $('#selectYAxis option[value='+DEFAULT_Y_VALUE+']').prop('selected', true);
    $('#selectYAxis').trigger("chosen:updated");
}


/**
 *
 * @param alertText
 * @param type
 * @returns {string}
 */
function getAlertHTMLString(alertText, type){
    return '<div class="alert alert-' + type + '"><a class="close" data-dismiss="alert">×</a><span>' +alertText + '</span></div>';
}

/**
 * Create a series for the given dataPoints
 * NOTE: turboThreshold is 1000 by default, and 0 disables it.
 *       please refer to http://api.highcharts.com/highcharts#plotOptions.series.turboThreshold
 * @param systemName - name of system
 * @param dataPoints - array of values for graph; [{x:"", y: "", date: "", marker: ""}]
 * @param graphType
 * @param id
 * @param linkedTo - used to group series to a system
 * @param i - The iterator for a measurement
 * @param j - The iterator for a system
 * @param yType - The measurement type name
 * @returns {{name: string, type: *, data: *, color: string, id: *, yAxis: *, dashStyle: string, marker: {symbol: string}}|*}
 */
function getDataPoints(systemName, dataPoints, graphType, id, linkedTo, color, yAxis, dashStyle, markerType, yType) {
    var series = { name: systemName + ',' + yType,
        type: graphType,
        data: dataPoints,
        color: color,
        id: id,
        yAxis: yAxis,
        //dashStyle: DASHSTYLES[j],
        dashStyle: dashStyle,
        turboThreshold:0,
        marker: {symbol: markerType}
    };
    if(linkedTo) {
        series.linkedTo = id;
    }
    return series;
}


/**
 *
 * @param yType - Y Value, used to label this axis
 * @param color - Color used to identify axis, and relate it to the color of the plotted data
 * @param opposite - Boolean, Determines which side of the chart the axis should be plotted on
 * @param units - Units for the given measurement type
 * @returns {{title: {text: *}, labels: {format: string, style: {color: *}}, opposite: boolean}}
 */
function createYAxis(yType, color, opposite, units){
    var unitLabel;

    // Determine how the units should be displayed for this variable
    if (units){
        unitLabel = (_.isEqual(units, "celsius")) ? "°C" : units;
    }else{
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


/**
 * Generates a list of Y Axes, copied from the overlay graph.
 * @param yAxes - List of selected y-axis values
 * @returns {Array}
 */
function copyYAxes(yAxes){
    var axesToAdd = [];
    _.each(yAxes, function(axis){
        var axisLabel = axis.userOptions.title.text;
        axesToAdd.push(createYAxis(
            axisLabel,
            axis.userOptions.title.style.color,
            axis.opposite));
    });
    return axesToAdd;
}


/**
 * Generate a list of the data series copied from the overlay graph
 *
 * @param series - The list of series stored in the overlay graph
 * @param systemID - System ID for which data is being copied
 * @returns {Array}
 */
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


/**
 * Toggles between the overlay and split modes.
 * The Split mode essentially copies over the series data for each system from the original overlay
 * chart to a number of new individual charts. One new chart per system.
 */
function toggleSplitMode(){
    // Can only split with 2+ systems
    if (selectedSystemIDs.length > 1) {

        // List of new charts
        var splitCharts = [];

        // Grab series and yAxes from the overlay chart
        var yAxes = CHART.yAxis;
        var series = CHART.series;

        _.each(selectedSystemIDs, function(systemID, k) {
            // Copy over formatting options from overlay chart
            var new_opts = HC_OPTIONS;

            new_opts.title.text = "NO DATA FOR THIS SYSTEM";
            new_opts.chart.renderTo = "chart-" + k;
            new_opts.yAxis = copyYAxes(yAxes);
            new_opts.series = copySeries(series, systemID);

            // Loop through series to extract system names and assign as titles. If there is no data
            // for a system, then the series will not exist and the name remains "NO DATA FOR THIS SYSTEM"
            for (var i=0; (i<series.length); i++){
                if(_.isEqual(systemID, series[i].userOptions.id)){
                    new_opts.title.text = series[i].name.split(",")[0].trim();
                }
            }

            // Add new split chart to list of charts
            var chart = new Highcharts.Chart(new_opts);
            splitCharts.push(chart);
        });

        // Draw the split charts
        _.each(splitCharts, function(chart){chart.redraw()});
    }
}


/* ##################################################################################################################
 PAGE-DRIVING FUNCTIONS
 ################################################################################################################### */

/**
 *  main - Sets behaviors for Submit and Reset buttons, populates y-axis dropdown, and checks nitrate as default y-axis
 */
function main(){

    // Select the default y-axis value
    setDefaultYAxis();

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
            toggleSplitMode();
        }
    });

    // When the submit button is clicked, redraw the graph based on user selections
    $('#submitbtn').on('click', function() {
        $('#alert_placeholder').empty();
        drawChart();

        // Check if the toggle is active. (i.e, overlay mode enabled)
        // If in split mode, make the split graphs
        if(!$('.toggle').data('toggles').active){
            toggleSplitMode();
        }
    });

    // Reset button, returns dropdowns to default, clears checklist, and displays default nitrate vs time graph
    $('#resetbtn').on('click', function(){

        // Reset X Axis selection to default
        $('#selectXAxis option').prop(SELECTED, function() {
            return this.defaultSelected;
        });

        // Reset Graph Type selection to default
        $('#selectGraphType option').prop(SELECTED, function() {
            return this.defaultSelected;
        });

        $('#selectStatus option').prop(SELECTED, function() {
            return this.defaultSelected;
        });

        $('#'+NUM_ENTRIES_ELEMENT_ID+' option').prop(SELECTED, function() {
            return this.defaultSelected;
        });

        $('#alert_placeholder').empty();

         $('[id^=chart-]').hide();
        $('#analyzeContainer').show();
        $('.toggle').data('toggles').toggle(true, false, true);

        // Select the default y-axis value
        setDefaultYAxis();

        drawChart();
    });

    $('#selectYAxis').bind("chosen:maxselected", function () {
        $('#alert_placeholder').html(getAlertHTMLString("You can select up to " + MAXSELECTIONS + " systems", 'danger'));
    });
}


/**
 *
 * loadChart - On window load, populates the Chart
 */
window.onload = function() {

    HC_OPTIONS = {
        chart: {
            renderTo: 'analyzeContainer',
            type: 'line',
            zoomType: 'xy',
            backgroundColor: BACKGROUND,
            plotBorderColor: '#606063'
        },
        title: {
            text: CHART_TITLE,
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
                text: XAXIS_TITLE,
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
        CHART = new Highcharts.Chart(HC_OPTIONS);
    }catch(err){
        console.log("Unable to initialize Highcharts Chart object!");
        console.log(err.stack);
    }
    Highcharts.setOptions(Highcharts.theme);
    // Render chart based on default page setting. i.e. x-axis & graph-type dropdowns, and the y-axis checklist
    drawChart();
};


/**
 * Using the metadata for a system and its measurements, generate HTML for the
 * Tooltips displayed at each datapoint on the plot
 * @returns {string}
 */
function tooltipFormatter(){
    // Series names are of the format "SystemName - MeasurementType" so we extract the name and type from here
    var tooltipInfo = this.series.name.split(",");
    var yVal = tooltipInfo[1];

    // Represent unitless features with "". And Celsius becomes "°C"
    var units = measurement_types_and_info[yVal].unit;
    units = (units) ? units : "";
    units = (_.isEqual(units, "celsius")) ? "°C" : units;

    // Capitalize measurement type
    yVal = yVal.charAt(0).toUpperCase() + yVal.slice(1);

    // Get local time and get the day, month, year, and time
    var datestr = this.point.date + SPACE + GMT;
    var datetime = new Date(datestr);
    var time = datetime.toTimeString();
    var day   = datetime.getDate(),
        month = datetime.getMonth()+1,
        year  = datetime.getFullYear();

    // Generate a readable description of any annotations for this datapoint
    var eventString = "";
    if (this.point.annotations) {
        console.log('event found');
        eventString = "<br><p>Most recent event(s): </p>";
        _.each(this.point.annotations, function (event) {
            console.log(event);
            var event_datetime = new Date(event.date + SPACE + GMT);
            eventString = eventString + '<br><p>' + annotationsMap[event.id]+ " at " + event_datetime.toString() + '<p>'
        });
    }

    return '<b>' + tooltipInfo[0] + '</b>' +
        '<br><p>' + yVal + ": " + this.y + ' ' + units + '</p>' +
        '<br><p>Hours in cycle: ' + this.x + '</p>' +
        '<br><p>Measured on: ' + month + '/' + day + '/' + year + '</p>' +
        '<br><p>At time: ' + time +'</p>' +
        eventString;
}
