/* ##################################################################################################################
 CONSTANTS
 ################################################################################################################### */

var XAXIS = "selectXAxis";
var YAXIS = "selectYAxis";
var XAXISVALUE = "";
var YAXISVALUE = "";
var OPTION = 'option';
var CHART = "";
var SHOW_IN_LEGEND = true;
var GRAPH_TYPE = "selectGraphType";
var CURSOR_TYPE = "pointer";
var ZOOM_ENABLED = true;
var TIME = "time";
var SELECTED = 'selected';
var CHECKED = "checked";
var UNCHECKED = "unchecked";
var LINE = "line";
var SCATTER = "scatter";
var BAR_CHART = "barchart";
var DEFAULT_Y_TEXT = "Nitrate";
var DEFAULT_Y_VALUE = DEFAULT_Y_TEXT.toLowerCase();
var CHART_TITLE = "System Analyzer";


/* ##################################################################################################################
 HELPER FUNCTIONS
 #################################################################################################################### */

/**
 *
 * @param graphType - Line or Scatter or Barchart
 * @param showLegend - boolean value (true or false)
 * @param systemName - name of system
 * @param dataPoints - array of values for graph; [{x:"", y: "", data: ""}]
 * @param content - HTML formatted String that populates dataPoint ToolTips
 * @returns {{type: *, showInLegend: *, name: *, dataPoints: *, content: *}}
 */
var getDataPoints = function(graphType, showLegend, systemName, dataPoints, content) {
    return {
        type: graphType,
        showInLegend: showLegend,
        name: systemName,
        dataPoints: dataPoints,
        toolTipContent: content
    };
};

var getDataPointsHC = function(systemName, dataPoints, color) {
    return {
        name: systemName,
        data: dataPoints,
        color: color
    };
};


// TODO: This will need to be re-evaluated to incorporate non-time x-axis values. For now, stubbing xType for this.
/**
 *
 * @param xType - X-axis values. Ex: Time, pH, Hardness
 * @param yType - Y-axis values. Ex: pH, Nitrate
 * @param graphType - Type of graph to display. Ex: line, scatter
 * @returns {Array} - An array of CanvasJS dataPoints of yType measurement data for all systems
 */
var getDataPointsForPlot = function(xType, yType, graphType){
    var dataPointsList = [];
    _.each(systems_and_measurements, function(system){
        var measurements = system.measurement;
        _.each(measurements, function(measurement){
            if (_.isEqual(measurement.type.toLowerCase(), yType.toLowerCase())){
                dataPointsList.push(
                    getDataPoints(
                        graphType,
                        SHOW_IN_LEGEND,
                        system.name,
                        measurement.values,
                        buildTooltipContent(xType, yType)
                    )
                );
            }
        });
    });
    return dataPointsList;
};

var getDataPointsForPlotHC = function(xType, yType, color){
    var dataPointsList = [];
    _.each(systems_and_measurements, function(system){
        var measurements = system.measurement;
        _.each(measurements, function(measurement){
            if (_.isEqual(measurement.type.toLowerCase(), yType.toLowerCase())){
                dataPointsList.push(
                    getDataPointsHC(
                        system.name,
                        measurement.values,
                        color
                    )
                );
            }
        });
    });
    return dataPointsList;
};


/**
 *
 * @param chart - A CanvasJS chart
 * @param xType - X-axis value chosen from dropdown
 * @param yTypeList - List of y-axis values selected from the checklist
 * @param graphType - The graph type chosen from dropdown
 */
var updateChartDataPoints = function(chart, xType, yTypeList, graphType){
    var newDataSeries = [];
    var activeMeasurements = getAllActiveMeasurements();
    var measurementsToFetch = _.difference(yTypeList, activeMeasurements);
    if (measurementsToFetch.length > 0) {
        console.log("Call API for " + measurementsToFetch);
        // Some AJAX function that grabs data from API or DB, then updates systems_and_measurements with the response
        // selectedSystemIDs is a global carried over from the view fxn
        // updateSystemsAndMeasurementsObject(selectedSystemIDs, measurementsToFetch);
    }
    _.each(yTypeList, function(yType){
        newDataSeries = newDataSeries.concat(getDataPointsForPlot(xType, yType, graphType));
    });
    chart.options.data = newDataSeries;
};

var updateChartDataPointsHC = function(chart, xType, yTypeList, color){
    var newDataSeries = [];
    var activeMeasurements = getAllActiveMeasurements();
    var measurementsToFetch = _.difference(yTypeList, activeMeasurements);
    if (measurementsToFetch.length > 0) {
        console.log("Call API for " + measurementsToFetch);
        // Some AJAX function that grabs data from API or DB, then updates systems_and_measurements with the response
        // selectedSystemIDs is a global carried over from the view fxn
        // updateSystemsAndMeasurementsObject(selectedSystemIDs, measurementsToFetch);
    }
    _.each(yTypeList, function(yType){
        newDataSeries = newDataSeries.concat(getDataPointsForPlot(xType, yType, color));
    });
    chart.options.data = newDataSeries;
};


/**
 *
 * @param xType - X-axis values. Ex: Time, pH, Hardness
 * @param yType - Y-axis values. Ex: pH, Nitrate
 * @returns HTML that populates dataPoint ToolTips with the specifics of a measurement
 */
var buildTooltipContent = function(xType, yType){
    if (xType === TIME.toLowerCase()){
        xType = "Hours since creation";
    }
    return "<h4>Measured on: {date}</h4> <p>" + xType + ": {x}</p> <p>" + yType + ": {y}</p>"
};


/**
 *
 * @returns {Array} - An array of all measurement types currently being stored
 */
var getAllActiveMeasurements = function() {
    // Grab all measurement types in the checklist
    var activeMeasurements = [];
    var systemMeasurements = _.first(systems_and_measurements).measurement;
    _.each(systemMeasurements, function(measurement){
        activeMeasurements.push(measurement.type.toLowerCase());
    });
    return activeMeasurements;
};


/**
 *
 * @returns {Array} - An array of all selected checkbox values
 */
var getAllYAxisSelections = function(){
    return $('#tokenize').tokenize().toArray();
};


/**
 *
 */
var drawChart = function(){
    var graphType = document.getElementById(GRAPH_TYPE).value;
    var xType = document.getElementById(XAXIS).value;

    // Get measurement types to display on the y-axis
    var yTypes = getAllYAxisSelections();
    var color = "blue";

    // Generate a data Series for each y-value type, and assign them all to the CHART
    updateChartDataPoints(CHART, xType, yTypes, graphType);
    //updateChartDataPointsHC(CHART, xType, yTypes, color);

    // TODO: What about the other chart characteristics? Symbols, ranges, different scales, different y-axes?

    // Render the new chart
    CHART.render();
};


/* ##################################################################################################################
 PAGE-DRIVING FUNCTIONS
 ################################################################################################################### */

/**
 *  main - Sets behaviors for Submit and Reset buttons, populates x-axis dropdown, and checks nitrate as default y-axis
 */
var main = function(){

    // Select the default y-axis value
    $('#tokenize').tokenize().tokenAdd(DEFAULT_Y_VALUE, DEFAULT_Y_TEXT);

    // When the submit button is clicked, redraw the graph based on user selections
    $('#submitbtn').click(function() {
        drawChart();
    });

    // Reset button, returns dropdowns to default, clears checklist, and displays defuault nitrate vs time graph
    $('#resetbtn').click(function(){

        // Reset X Axis selection to default
        $('#selectXAxis option').prop(SELECTED, function() {
            return this.defaultSelected;
        });

        // Reset Graph Type selection to default
        $('#selectGraphType option').prop(SELECTED, function() {
            return this.defaultSelected;
        });

        // Uncheck all Y Axis checkboxes except DEFAULT_Y
        $('#tokenize').tokenize().clear();
        $('#tokenize').tokenize().tokenAdd(DEFAULT_Y_VALUE, DEFAULT_Y_TEXT);

        drawChart();
    });
};


/**
 *
 * loadChart - On window load, populates the Chart
 */
window.onload = function() {

    // Create our default chart
    CHART = new CanvasJS.Chart("analyzeContainer", {
        title :{
            text : "My CanvasJS"
        },
        // TODO: This will change, we need a procedure for setting min/max ranges based on XType
        // TODO: Also need to take into consideration ranges for YType
        axisX : {
            minimum : 0
        },
        legend : {
            cursor : CURSOR_TYPE,
            itemclick : function (e)
            {
                if (typeof (e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
                    e.dataSeries.visible = false;
                } else {
                    e.dataSeries.visible = true;
                }
                e.chart.render();
            }
        },
        zoomEnabled : ZOOM_ENABLED,
        data : []
    });
    // Render chart based on default page setting. I.e. x-axis & graph-type dropdowns, and the y-axis checklist
    drawChart();
};