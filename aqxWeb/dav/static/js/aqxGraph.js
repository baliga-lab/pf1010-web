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
var HC_OPTIONS;
var COLORS = Highcharts.getOptions().colors; // Contains 10 different colors; .symbols contains 5 symbols
var MARKERS = {'nitrate': 'circle', 'ph': 'url(https://www.highcharts.com/samples/graphics/snow.png)', 'Ammonia': 'triangle-down', 'Nitrite': 'square'}
    //'triangle','diamond' ,'url(https://www.highcharts.com/samples/graphics/sun.png']


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
var getDataPointsHC = function(systemName, dataPoints, color, graphType, id, linkedTo) {
    series = { name: systemName,
               type: graphType,
               data: dataPoints,
               color: color,
               id: id
    };
    if(linkedTo) {
        series.linkedTo = id;
    }
    return series;
};

// TODO: This can be done before plotting graph
var addMarker = function(dataPoints, type) {
    var symbolType =  MARKERS[type];
    _.each(dataPoints, function(data) {
        data.marker = {'symbol': symbolType};
    })
    return dataPoints;
}

// TODO: This will need to be re-evaluated to incorporate non-time x-axis values. For now, stubbing xType for this.
/**
 *
 * @param xType - X-axis values. Ex: Time, pH, Hardness
 * @param yType - Y-axis values. Ex: pH, Nitrate
 * @param graphType - Type of graph to display. Ex: line, scatter
 * @returns {Array} - An array of CanvasJS dataPoints of yType measurement data for all systems
 */
var getDataPointsForPlotHC = function(xType, yTypeList, color, graphType){

    var dataPointsList = [];
    // Every system should be represented by unique color
    // Each measurementType should have a unique marker type

    var colorCounter = 0, markerCounter = 0;
    _.each(systems_and_measurements, function(system){
        var measurements = system.measurement;
        var linkedTo = false;
        _.each(measurements, function(measurement){
            _.each(yTypeList, function(yType) {
                if (_.isEqual(measurement.type.toLowerCase(), yType.toLowerCase())){
                    datawithMarkers = addMarker(measurement.values, yType);
                    dataPointsList.push(
                        // TODO: Discuss about outOfBoundExceptions while using COLORS and MARKERS
                        getDataPointsHC(system.name, datawithMarkers, COLORS[colorCounter],
                                        graphType, system.system_uid,linkedTo));
                    linkedTo = true;
                }
            });
        });
        colorCounter++;
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
var updateChartDataPointsHC = function(chart, xType, yTypeList, color, graphType){
    var newDataSeries = [];
    var activeMeasurements = getAllActiveMeasurements();
    var measurementsToFetch = _.difference(yTypeList, activeMeasurements);
    if (measurementsToFetch.length > 0) {
        console.log("Call API for " + measurementsToFetch);
        // Some AJAX function that grabs data from API or DB, then updates systems_and_measurements with the response
        // selectedSystemIDs is a global carried over from the view fxn
        // updateSystemsAndMeasurementsObject(selectedSystemIDs, measurementsToFetch);
    }
    //_.each(yTypeList, function(yType){
    //    newDataSeries = newDataSeries.concat(getDataPointsForPlotHC(xType, yType, color, graphType));
    //});
    newDataSeries = getDataPointsForPlotHC(xType, yTypeList, color, graphType);
    while(chart.series.length > 0)
        chart.series[0].remove(true);

    _.each(newDataSeries, function(series) {
        chart.addSeries(series);
    });
    return chart;
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

var setDefaultYAxis = function() {
    $(".js-example-basic-multiple").val(DEFAULT_Y_VALUE).select2({
        maximumSelectionLength: 4
    });
};


/**
 *
 */
var drawChart = function(){
    var graphType = document.getElementById(GRAPH_TYPE).value;
    var xType = document.getElementById(XAXIS).value;

    // Get measurement types to display on the y-axis
    var yTypes = $(".js-example-basic-multiple").select2().val();
    var color = "blue";

    // Generate a data Series for each y-value type, and assign them all to the CHART
    updateChartDataPointsHC(CHART, xType, yTypes, color, graphType).redraw();

    // TODO: What about the other chart characteristics? Symbols, ranges, different scales, different y-axes?

    // Render the new chart
    //CHART.redraw();
};


/* ##################################################################################################################
 PAGE-DRIVING FUNCTIONS
 ################################################################################################################### */

/**
 *  main - Sets behaviors for Submit and Reset buttons, populates x-axis dropdown, and checks nitrate as default y-axis
 */
var main = function(){

    // When the submit button is clicked, redraw the graph based on user selections
    $('#submitbtn').click(function() {
        drawChart();
    });

    // Select the default y-axis value
    setDefaultYAxis();

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
        setDefaultYAxis();

        drawChart();
    });
};


/**
 *
 * loadChart - On window load, populates the Chart
 */
window.onload = function() {

     HC_OPTIONS = {
       chart: {
           renderTo: 'analyzeContainer',
           type: 'line',
           zoomType: 'xy'
       },
       xAxis: {
           minPadding: 0.05,
           maxPadding: 0.05
       },
       showInLegend: true,
       series: []
    };
    CHART = new Highcharts.Chart(HC_OPTIONS);

    // Render chart based on default page setting. i.e. x-axis & graph-type dropdowns, and the y-axis checklist
    drawChart();
};