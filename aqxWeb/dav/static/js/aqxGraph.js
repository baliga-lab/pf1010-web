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
var MARKERS = Highcharts.getOptions().symbols;
//Dashstyle is applicable only to line, spline, area and scatter graphs
var DASHSTYLES = ["Solid", "ShortDash", "ShortDot", "ShortDashDot", "ShortDashDotDot", "Dot", "Dash", "LongDash", "DashDot", "LongDashDot", "LongDashDotDot"];
//var MARKERS = {'nitrate': 'circle', 'ph': 'url(https://www.highcharts.com/samples/graphics/snow.png)', 'Ammonia': 'triangle-down', 'Nitrite': 'square'}
//'triangle','diamond' ,'url(https://www.highcharts.com/samples/graphics/sun.png']


/* ##################################################################################################################
 HELPER FUNCTIONS
 #################################################################################################################### */

/**
 *
 * @param systemName - name of system
 * @param dataPoints - array of values for graph; [{x:"", y: "", date: "", marker: ""}]
 * @param color - color of the series
 * @param graphType - Line or Scatter or Barchart
 * @param id - systemId
 * @param linkedTo - used to group series to a system
 * @param yAxis - The axis these graph will be plotted against
 * @returns {{name: *, type: *, data: *, color: *, id: *}|*}
 */
var getDataPointsHC = function(systemName, dataPoints, color, graphType, id, linkedTo, yAxis, dashStyleIndex) {
    series = { name: systemName,
        type: graphType,
        data: dataPoints,
        color: color,
        id: id,
        yAxis: yAxis,
        dashStyle: DASHSTYLES[dashStyleIndex]
    };
    if(linkedTo) {
        series.linkedTo = id;
    }
    return series;
};

// TODO: This can be done before plotting graph
/**
 *
 * @param dataPoints - array of values for graph; [{x:"", y: "", date: ""}]
 * @param type - measurementType. Ex: nitrate, ph
 * @returns datapoints with new 'marker' attribute [{x:"", y: "", date: "", marker: ""}]
 */
var addMarker = function(dataPoints, markerIndex) {
    var symbolType =  MARKERS[markerIndex];
    _.each(dataPoints, function(data) {
        data.marker = {'symbol': symbolType};
    });
    return dataPoints;
};

/**
 *
 * @param yTypeList
 * @returns {{}}
 */
var createYAxisMap = function(yTypeList) {
    var axisMap = {}, yAxis = 0;
    _.each(yTypeList, function(x){
        axisMap[x] = yAxis++;
    });
    return axisMap;
};

var randomlyAssignMarkers = function(yTypeList) {
    var typeAndSymbol = {};
    _.each(yTypeList, function(yType) {
        typeAndSymbol[yType] = Math.floor((Math.random() * (MARKERS.length -1)) + 1);
    });
    return typeAndSymbol;
}

var randomlyAssignLineStyleForSystems = function(systems) {
    var systemAndDashline = {};
    _.each(systems, function(system) {
        systemAndDashline[system.system_uid] = Math.floor((Math.random() * (DASHSTYLES.length - 1)) + 1);
    });
    return systemAndDashline;
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
    var markerForMeasurement = randomlyAssignMarkers(yTypeList);
    var dashStyleForSystems = randomlyAssignLineStyleForSystems(systems_and_measurements);
    var axisMap = createYAxisMap(yTypeList);
    //TODO: Rename systems_and_measurements to selectedSystemsToAnalyze
    //TODO: It is possible to remove axisMap and use function(system, i)
    _.each(systems_and_measurements, function(system){
        var measurements = system.measurement;
        // Used to link measurements to system
        var linkedTo = false;
        _.each(yTypeList, function(yType) {
            _.each(measurements, function(measurement){
                if (_.isEqual(measurement.type.toLowerCase(), yType.toLowerCase())){
                    var systemId = system.system_uid;
                    datawithMarkers = addMarker(measurement.values, markerForMeasurement[yType]);
                    //TODO: You can add yaxis here
                    dataPointsList.push(
                        // TODO: Discuss about outOfBoundExceptions while using COLORS and MARKERS
                        getDataPointsHC(system.name, datawithMarkers, COLORS[colorCounter],
                            graphType, systemId,linkedTo, axisMap[yType], dashStyleForSystems[systemId]));
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
 * @param yType
 * @param numAxes
 * @returns {{title: {text: *}, labels: {format: string, style: {color: *}}, opposite: boolean}}
 */
var createYAxis = function(yType, numAxes){
    return { // Primary yAxis
        title:
        {
            text: yType
        },
        labels:
        {
            format: '{value} ',
            style: { color: COLORS[Math.floor((Math.random() * 10) + 1)] }
        },
        opposite: (numAxes % 2 === 0)
    }
};

/**
 *
 * @param chart - A CanvasJS chart
 * @param xType - X-axis value chosen from dropdown
 * @param yTypeList - List of y-axis values selected from the checklist
 * @param graphType - The graph type chosen from dropdown
 */
var updateChartDataPointsHC = function(chart, xType, yTypeList, color, graphType){
    var activeMeasurements = getAllActiveMeasurements();
    var measurementsToFetch = _.difference(yTypeList, activeMeasurements);
    var measurementIDList = [];
    _.each(measurementsToFetch, function(measurement){
        measurementIDList.push(measurement_types_and_ids[measurement]);
    });
    console.log(measurementIDList);
    console.log(selectedSystemIDs);

    if (measurementsToFetch.length > 0) {
        console.log("Call API for " + measurementsToFetch);
        $(function(){
            $.ajax({
                type: 'POST',
                contentType: 'application/json;charset=UTF-8',
                dataType: 'json',
                async: false,
                url: '/dav/aqxapi/get/readings/time_series_plot',
                data: JSON.stringify({systems: selectedSystemIDs, measurements: measurementIDList}, null, '\t'),
                success: function(data){
                    console.log('success',data);
                    var systems = data.response;
                    _.each(systems, function(system){
                        var systemMeasurements = system.measurement;
                        _.each(systems_and_measurements, function(existingSystem){
                            if (_.isEqual(existingSystem.system_uid, system.system_uid)){
                                existingSystem.measurement = existingSystem.measurement.concat(systemMeasurements);
                            }
                        });
                    });
                    console.log(systems_and_measurements);
                }
            });
        });
        // Some AJAX function that grabs data from API or DB, then updates systems_and_measurements with the response
        // selectedSystemIDs is a global carried over from the view fxn
        // updateSystemsAndMeasurementsObject(selectedSystemIDs, measurementsToFetch);
    }
    console.log("here");
    chart.xAxis[0].setTitle({ text: xType });
    var numYAxes = 1;

    chart = clearOldGraphValues(chart);

    _.each(yTypeList, function(yType){
        // If axis with these units not already up...
        chart.addAxis(createYAxis(yType, numYAxes));
        numYAxes++;
    });

    var newDataSeries = getDataPointsForPlotHC(xType, yTypeList, color, graphType);
    _.each(newDataSeries, function(series) {
        chart.addSeries(series);
    });

    return chart;
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
 *
 */
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
    console.log(xType);

    // Generate a data Series for each y-value type, and assign them all to the CHART
    updateChartDataPointsHC(CHART, xType, yTypes, color, graphType).redraw();

    // TODO: What about the other chart characteristics? Symbols, ranges, different scales, different y-axes?
    addMeasurementLegend();
    //REMOVELEGENDSYMBOL(CHART);
};

var addMeasurementLegend = function() {
    var selectedMeasurements = $(".js-example-basic-multiple").select2().val();
    $('#legendTypes').remove();
    $('#measurementLegend').append('<div id="legendTypes"></div>');
    _.each(selectedMeasurements, function (measurement) {
        var symbol;
        switch (measurement.toLowerCase()) {
            case 'nitrate':
                symbol = '●';
                break;
            case 'ph':
                symbol = '<img src="https://www.highcharts.com/samples/graphics/snow.png" alt="Marker" />';
                break;
            case 'square':
                symbol = '■';
                break;
            case 'triangle':
                symbol = '▲';
                break;
            case 'triangle-down':
                symbol = '▼';
                break;
        }
        $('#legendTypes').append('<div>' + measurement+ '<span>' + symbol +'</span></div>');
    });
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
        //setDefaultYAxis();
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
            zoomType: 'xy'
        },
        legend: {
            align: 'right',
            verticalAlign: 'top',
            layout: 'vertical',
            x: 0,
            y: 100,
            labelFormatter: function() {
                return '<span style="color: '+this.color+'">'+ this.name + '</span>';
            }
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

var REMOVELEGENDSYMBOL = function(chart){
    var series = chart.series;
    $(series).each(function(i, s){
        if (s.legendSymbol)
            s.legendSymbol.destroy();
        if (s.legendLine)
            s.legendLine.destroy();
    });
};