// Constants
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
var TIME = "Time";
var NITRATE = "Nitrate";

/**
 *
 * @param graphType - line or Splatter or bar
 * @param showLegend - boolean value (true or false)
 * @param systemName - name of system
 * @param dataPoints - array of values for graph; [{x:"", y: "", data: ""}]
 * @returns {{type: *, showInLegend: *, name: *, dataPoints: *}}
 */
var getDataPoints = function(graphType, showLegend, systemName, dataPoints) {
    var canvasDataPoints = {
        type: graphType,
        showInLegend: showLegend,
        name: systemName,
        dataPoints: dataPoints
    };
    return canvasDataPoints;
};

// TODO: This will need to be re-evaluated to incorporate non-time x-axis values. For now, stubbing xType for this.
/**
 *
 * @returns
 * @param xType - X-axis values. Ex: Time, pH, Hardness
 * @param yType - Y-axis values. Ex: pH, Nitrate
 * @param graphType - Type of graph to display. Ex: line, scatter
 * @returns {Array} - An array of CanvasJS dataPoints of yType measurement data for all systems
 */
var getDataPointsForPlot = function(xType, yType, graphType){
    var dataPointsList = [];
    _.each(systems_and_measurements, function(systemMeasurements){
        var measurements = systemMeasurements.measurement;
        _.each(measurements, function(measurement){
            if (_.isEqual(measurement.type.toLowerCase(), yType.toLowerCase())){
                dataPointsList.push(
                    getDataPoints(graphType, SHOW_IN_LEGEND, systemMeasurements.name, measurement.values)
                );
            }
        });
    });
    return dataPointsList;
};

/**
 *
 * @param xType - X-axis values. Ex: Time, pH, Hardness
 * @param yType - Y-axis values. Ex: pH, Nitrate
 * @returns HTML that populates dataPoint ToolTips with the specifics of a measurement
 */
var buildTooltipContent = function(xType, yType){
    if (xType === TIME){
        xType = "Hours since creation";
    }
    return "<h4>Measured on: {date}</h4> <p>" + xType + ": {x}</p> <p>" + yType + ": {y}</p>"
};

window.onload = function () {

    //Grabs the default XAxis type, time, and the default YAxis type, pH
    //var selected_yvalue_type = document.getElementById("selectYAxis").value;
    //var selected_xvalue_type = document.getElementById("selectXAxis").value;

    var selected_yvalue_type = NITRATE.toLowerCase();
    var selected_xvalue_type = TIME.toLowerCase();

    //Grabs the default graph type from the Graph Style selection dropdown
    var graph_type = document.getElementById(GRAPH_TYPE).value;

    // Get the default nitrate vs. time dataPoints
    var dataPoints = getDataPointsForPlot(selected_xvalue_type, selected_yvalue_type, graph_type);

    // Create our default chart which plots nitrate vs. time
    CHART = new CanvasJS.Chart("analyzeContainer", {
        title :{
            text : "My CanvasJS"
        },
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
        toolTip : {
            content : buildTooltipContent(selected_xvalue_type, selected_yvalue_type)
        },
        zoomEnabled : ZOOM_ENABLED,
        data : dataPoints
    });

    // Render the default chart
    CHART.render();

    // Fill x-value dropdown with all measurement types, plus time
    populateDropdown(XAXIS, [TIME].concat(dropdown_values));
};

/**
 *
 */
var main = function(){

    // When the submit button is clicked, redraw the graph based on user selections
    $('#submitbtn').click(function() {
        var graphType = document.getElementById(GRAPH_TYPE).value;
        var xType = document.getElementById(XAXIS).value;

        // Get measurement types to display on the y-axis
        var yTypes = [];
        _.each($('#listOfYAxisValues input:checked'), function(checkedInput){
            yTypes.push(checkedInput.value.toLowerCase());
        });

        // Generate a data Series for each y-value type, and assign them all to the CHART
        var newDataSeries = [];
        _.each(yTypes, function(type){
            newDataSeries = newDataSeries.concat(getDataPointsForPlot(xType, type, graphType));
        });
        CHART.options.data = newDataSeries;

        // Render the new chart
        CHART.render();
    });
};

/**
 * Populates dropdown menus for each metadata category
 *
 * @param elementId - Id of the dropdown to populate
 * @param measurement_data_object - Object containing unique measurement types. Ex: pH, nitrate, time
 */
var populateDropdown = function(elementId, measurement_data_object){
    var select = document.getElementById(elementId);
    _.each(measurement_data_object, function(measurement_type){
        var el = document.createElement(OPTION);
        el.textContent = measurement_type;
        el.value = measurement_type.toLowerCase();
        select.appendChild(el);
    });
};