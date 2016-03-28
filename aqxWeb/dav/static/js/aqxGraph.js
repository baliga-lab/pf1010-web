/* ##################################################################################################################
 CONSTANTS
 ################################################################################################################### */

var XAXIS = "selectXAxis";
var CHART = "";
var GRAPH_TYPE = "selectGraphType";
var SELECTED = 'selected';
var DEFAULT_Y_TEXT = "Nitrate";
var DEFAULT_Y_VALUE = DEFAULT_Y_TEXT.toLowerCase();
var CHART_TITLE = "System Analyzer";
var HC_OPTIONS;
var COLORS = ["lime", "orange", '#f7262f', "lightblue"];
var DASHSTYLES = ['Solid', 'LongDash', 'ShortDashDot', 'ShortDot', 'LongDashDotDot'];
var MARKERTYPES = ["circle", "square", "diamond", "triangle", "triangle-down"];
var BACKGROUND = {
    linearGradient: { x1: 0, y1: 0, x2: 1, y2: 1 },
    stops: [
        [0, '#2a2a2b'],
        [1, '#3e3e40']
    ]
};

/* ##################################################################################################################
 MAIN CHART LOADING FUNCTIONS
 #################################################################################################################### */

/**
 *
 */
var drawChart = function(){
    var graphType = document.getElementById(GRAPH_TYPE).value;
    var xType = document.getElementById(XAXIS).value;

    // Get measurement types to display on the y-axis
    var yTypes = $("#selectYAxis").val();

    // Generate a data Series for each y-value type, and assign them all to the CHART
    updateChartDataPointsHC(CHART, xType, yTypes, graphType).redraw();
};


/**
 *
 * @param chart - A CanvasJS chart
 * @param xType - X-axis value chosen from dropdown
 * @param yTypeList - List of y-axis values selected from the checklist
 * @param graphType - The graph type chosen from dropdown
 */
var updateChartDataPointsHC = function(chart, xType, yTypeList, graphType){

    // Clear the old chart's yAxis and dataPoints. Unfortunately this must be done manually.
    chart = clearOldGraphValues(chart);

    // Determine if any measurements are not already tracked in systems_and_measurements
    var activeMeasurements = getAllActiveMeasurements();
    var measurementsToFetch = _.difference(yTypeList, activeMeasurements);

    // If there are any measurements to fetch, get the ids then pass those to the API along with the system names
    // and add the new dataPoints to the systems_and_measurements object
    if (measurementsToFetch.length > 0) {
        var measurementIDList = [];
        _.each(measurementsToFetch, function(measurement){
            measurementIDList.push(measurement_types_and_info[measurement].id);
        });
        callAPIForNewData(measurementIDList);
    }

    // Handle the x axis, for now just using time
    // TODO: Expand to handle changing x axes
    chart.xAxis[0].setTitle({ text: "hours since creation" });

    // Get dataPoints and their configs for the chart, using systems_and_measurements and add them
    var newDataSeries = getDataPointsForPlotHC(chart, xType, yTypeList, graphType);
    _.each(newDataSeries, function(series) {
        chart.addSeries(series);
    });

    return chart;
};


// TODO: This will need to be re-evaluated to incorporate non-time x-axis values. For now, stubbing xType for this.
/**
 *
 * @param xType - X-axis values. Ex: Time, pH, Hardness
 * @param yTypeList - Y-axis values. Ex: [pH, Nitrate]
 * @param colorSchemeForMeasurement - {"nitrate": COLORS_INDEX, "pH": COLORS_INDEX}
 * @param markerForMeasurement = {"nitrate": MARKERS_INDEX, "pH": MARKERS_INDEX}
 * @param graphType - Type of graph to display. Ex: line, scatter
 * @returns {Array} - An array of dataPoints of yType measurement data for all systems
 */
var getDataPointsForPlotHC = function(chart, xType, yTypeList, graphType){

    // DataPoints to add to chart
    var dataPointsList = [];

    // Any y variables and systems that have missing data
    var missingYTypes = [];

    // Assign each axis a variable and an id
    var numAxes = 0;

    // Axis dict ensures that each variable is plotted to the same, unique axis for that variable
    var axes = {};
    _.each(yTypeList, function(axis){
        axes[axis] = {isAxis:false};
    });

    // Begin iterating through the systems
    _.each(systems_and_measurements, function(system, j){

        var measurements = system.measurement;
        // Used to link measurements to the same system
        var linkedTo = false;

        // Loop through selected measurement types
        _.each(yTypeList, function(yType) {

            // Then find matching types in the systems_and_measurements object
            _.each(measurements, function(measurement){
                if (_.isEqual(measurement.type.toLowerCase(), yType.toLowerCase())) {
                    var systemId = system.system_uid;

                    // Check if there is data for this system and measurement type
                    if (measurement.values.length > 0){

                        // Has this variable been assigned an axis yet?
                        // If not, create the axis and assign to a variable. This variables isAxis is now true,
                        // an axis is assigned, and the numAxes increments
                        if (!axes[yType].isAxis) {
                            chart.addAxis(createYAxis(yType, numAxes, measurement_types_and_info[yType].unit));
                            axes[yType].isAxis = true;
                            axes[yType].axis = numAxes++;
                        }

                        // Push valid dataPoints and their configs to the list of dataPoints to plot
                        dataPointsList.push(
                            getDataPoints(system.name, measurement.values, graphType, systemId, linkedTo, axes[yType].axis, j, yType));
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
        $('#alert_placeholder').html(getAlertHTMLString(missingYTypes));
    }
    return dataPointsList;
};


/* ##################################################################################################################
 AJAX CALLS TO GRAB NEW DATA
 #################################################################################################################### */


/**
 *
 * @param data
 */
var addNewMeasurementData = function(data){
    console.log('success',data);
    var systems = data.response;

    // Loop through existing systems in the systems_and_measurements object
    _.each(systems, function(system){
        var systemMeasurements = system.measurement;
        _.each(systems_and_measurements, function(existingSystem){
            // Match systems in the new data by id, and then add the new measurements
            // to the list of existing measurements
            if (_.isEqual(existingSystem.system_uid, system.system_uid)){
                existingSystem.measurement = existingSystem.measurement.concat(systemMeasurements);
            }
        });
    });
};


/**
 *
 * @param measurementIDList
 */
var callAPIForNewData = function(measurementIDList){
    $(function(){
        $.ajax({
            type: 'POST',
            contentType: 'application/json;charset=UTF-8',
            dataType: 'json',
            async: false,
            url: '/dav/aqxapi/get/readings/time_series_plot',
            data: JSON.stringify({systems: selectedSystemIDs, measurements: measurementIDList}, null, '\t'),
            success: function(data){
                addNewMeasurementData(data);
            }
        });
    });
};


/* ##################################################################################################################
 HELPER FUNCTIONS
 #################################################################################################################### */


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
 * @param chart
 * @returns {*}
 */
var clearOldGraphValues = function(chart) {
    // Clear yAxis
    while(chart.yAxis.length > 0){
        chart.yAxis[0].remove(true);
    }
    // Clear series data
    while(chart.series.length > 0) {
        chart.series[0].remove(true);
    }
    return chart;
};


/**
 * Returns the Y Axis text selector to default
 */
var setDefaultYAxis = function() {
    $("#selectYAxis").dropdown({
        maxSelections: 4
    });
    $("#selectYAxis").dropdown('clear');
    $("#selectYAxis").dropdown('set selected', DEFAULT_Y_VALUE);
};


/**
 *
 * @param missingYTypes
 * @returns {string}
 */
var getAlertHTMLString = function(missingYTypes){
    return '<div class="alert alert-danger"><a class="close" data-dismiss="alert">×</a><span>Missing values for: ' +
        _.uniq(missingYTypes).toString() + '</span></div>';
};

/**
 *
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
var getDataPoints = function(systemName, dataPoints, graphType, id, linkedTo, i, j, yType) {
    series = { name: systemName + ',' + yType,
        type: graphType,
        data: dataPoints,
        color: COLORS[i],
        id: id,
        yAxis: i,
        dashStyle: DASHSTYLES[j],
        marker: {symbol: MARKERTYPES[j]}
    };
    if(linkedTo) {
        series.linkedTo = id;
    }
    return series;
};


/**
 *
 * @param yType
 * @param axisNum
 * @param units
 * @returns {{title: {text: *}, labels: {format: string, style: {color: *}}, opposite: boolean}}
 */
var createYAxis = function(yType, axisNum, units){
    var unitLabel;
    if (units){
        unitLabel = (_.isEqual(units, "celsius")) ? "°C" : units;
    }else{
        unitLabel = "";
    }
    var color = COLORS[axisNum];
    return { // Primary yAxis
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
        opposite: axisNum % 2,
        gridLineColor: '#707073',
        lineColor: '#707073',
        minorGridLineColor: '#505053',
        tickColor: '#707073'
    };
};


/* ##################################################################################################################
 PAGE-DRIVING FUNCTIONS
 ################################################################################################################### */

/**
 *  main - Sets behaviors for Submit and Reset buttons, populates x-axis dropdown, and checks nitrate as default y-axis
 */
var main = function(){

    // Select the default y-axis value
    setDefaultYAxis();

    // When the submit button is clicked, redraw the graph based on user selections
    $('#submitbtn').click(function() {
        $('#alert_placeholder').empty();
        drawChart();
    });

    // Reset button, returns dropdowns to default, clears checklist, and displays default nitrate vs time graph
    $('#resetbtn').click(function(){

        // Reset X Axis selection to default
        $('#selectXAxis option').prop(SELECTED, function() {
            return this.defaultSelected;
        });

        // Reset Graph Type selection to default
        $('#selectGraphType option').prop(SELECTED, function() {
            return this.defaultSelected;
        });

        $('#alert_placeholder').empty();

        // Select the default y-axis value
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
            maxPadding: 0.05
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
    CHART = new Highcharts.Chart(HC_OPTIONS);
    Highcharts.setOptions(Highcharts.theme);
    // Render chart based on default page setting. i.e. x-axis & graph-type dropdowns, and the y-axis checklist
    drawChart();
};

var tooltipFormatter = function(){
    var tooltipInfo = this.series.name.split(",");
    var yVal = tooltipInfo[1];
    var units = measurement_types_and_info[yVal].unit;
    units = (units) ? units : "";
    units = (_.isEqual(units, "celsius")) ? "°C" : units;
    yVal = yVal.charAt(0).toUpperCase() + yVal.slice(1);
    var datetime = this.point.date.split(" ");
    return '<b>' + tooltipInfo[0] + '</b>' +
        '<br><p>' + yVal + ": " + this.y + ' ' + units + '</p>' +
        '<br><p>Hours in cycle: ' + this.x + '</p>' +
        '<br><p>Measured on: ' + datetime[0] + '</p>' +
        '<br><p>At time: ' + datetime[1] +'</p>';
};
