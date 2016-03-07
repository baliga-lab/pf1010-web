// Constants
var XAXIS = "selectXAxis";
var YAXIS = "selectYAxis";
var XAXISVALUE = "";
var YAXISVALUE = "";
var OPTION = 'option';
var CHART = "";

var addDataPointsToPlot = function(xType, yType, graphType){
    // Plots a graph for the given systems of type "graph_type" and with y-value "selected_measurement_type"
    _.each(systems_and_measurements, function(system_and_measurements){
        var measurements = system_and_measurements.measurement;
        _.each(measurements, function(measurement){
            if (measurement.type === selected_measurement_type){
                var new_plot = {
                    type : graph_type,
                    showInLegend : true,
                    name : system_and_measurements.name,
                    dataPoints : measurement.values
                };
                system_plot_data.push(new_plot);
            }
        });
    });
};

window.onload = function () {
    //data = request.get_json();

    var system_plot_data = [];

    //TODO: Function to grab desired measurement type
    var selected_measurement_type = "pH";

    //TODO: Function to grab graph type
    var graph_type = "line";

    // Plots a graph for the given systems of type "graph_type" and with y-value "selected_measurement_type"
    _.each(systems_and_measurements, function(system_and_measurements){
        var measurements = system_and_measurements.measurement;
        _.each(measurements, function(measurement){
            if (measurement.type === selected_measurement_type){
                var new_plot = {
                    type : graph_type,
                    showInLegend : true,
                    name : system_and_measurements.name,
                    dataPoints : measurement.values
                };
                system_plot_data.push(new_plot);
            }
        });
    });

    CHART = new CanvasJS.Chart("analyzeContainer", {
        title:{
            text: "My CanvasJS"
        },
        legend: {
            cursor: "pointer",
            itemclick: function (e)
            {
                if (typeof (e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
                    e.dataSeries.visible = false;
                } else {
                    e.dataSeries.visible = true;
                }
                e.chart.render();
            }
        },
        toolTip: {
            content: "<h4>Measured on: {date}</h4> <p>Hours since start: {x}</p> <p>" + selected_measurement_type + ": {y}</p>"
        },
        zoomEnabled: true,
        data:system_plot_data

        //data:
        //[
        //     {
        //        type: "line",
        //        showInLegend: true, name : 'System - 24',
        //        dataPoints: [
        //          { x:31, date:new Date(1970, 9, 29, 7), y:4},
        //          { x:32, date:new Date(1970, 9, 29, 2), y:1.3},
        //          { x:33, date:new Date(1970, 9, 29, 3), y:1.7},
        //          { x:44, date:new Date(1970, 9, 29, 6), y:1.92},
        //          { x:45, date:new Date(1970, 9, 29, 12), y:4.92},
        //          { x:48, date:new Date(1971, 4, 14, 15), y:1.7}
        //        ]
        //     },
        //
        //]
    });
    CHART.render();
};


//$(function() {
//
////  Populate X axis dropdown
//    populateDropdown(XAXIS, measurement_data_info);
//
////  Get selected values from dropdown
//    $("#" +XAXIS).change(function () {
//        XAXISVALUE  = $('option:selected', this).text();
//        plotGraph(XAXISVALUE);
//    });
//});

// Used to populate the x axis
var populateDropdown = function(elementId, measurement_data_object){
    var select = document.getElementById(elementId);
    _.each(measurement_data_object, function(measurement_type){
        var el = document.createElement(OPTION);
        el.textContent = measurement_type;
        el.value = measurement_type;
        select.appendChild(el);
    });
};

/**
 * Adds new data point to graph when dropdown changes
 * @param xAxisVal - selected value from dropdown
 */
var plotGraph = function(xAxisVal) {
    console.log(xAxisVal + "  ");
    //  Enter only if both the dropdowns are not null
     if(!(_.isEmpty(XAXISVALUE))) {
        // To add new datapoint to graph
         var dps = dataPointWrapper(metadataFromDB, 'system_1234', XAXISVALUE);
         CHART.options.data.push(createDataPoint("line", "true", "system_1234", dps ));
         CHART.render();
    }
};

/**
 *
 * @param graphType - line or Splatter or bar
 * @param showLegend - boolean value (true or false)
 * @param systemName - name of system
 * @param dataPoints - array of values for graph; [{x:"", y: "", data: ""}]
 * @returns {{type: *, showInLegend: *, name: *, dataPoints: *}}
 */
var createDataPoint = function(graphType, showLegend, systemName, dataPoints) {
    var dp = {
        type: graphType,
        showInLegend: showLegend,
        name: systemName,
        dataPoints: dataPoints
    }
    return dp;
}

/**
 *
 * @param metaData - measurement info for systems
 * @param systemUID - systemUID
 * @param measurementType - Eg: pH, Nitrate
 * @returns An array of a particular measurementType for a given systemUID
 */
var dataPointWrapper = function(metaData, systemUID, measurementType) {
    var result = "";
    _.each(metaData, function(system) {
       if(_.isEqual(system.name, systemUID)) {
           var measurements = system.measurement;
           _.each(measurements, function(measurement) {
               if(_.isEqual(measurement.type, measurementType)) {
                   result =  measurement.values;
               }
           })
       }
    });
    return result;
};

// TODO: Remove these dummy data
var measurement_data_info = ['pH', "nitrate", "Ammo"];


var metadataFromDB = [
    { name: 'system_1234' ,
      measurement: [
          { type: 'pH',
            values:
             [{ x:2, date:new Date(1970, 10, 12, 2), y:1.33},
              { x:7, date:new Date(1970, 10, 13, 3), y:2.17},
              { x:11, date:new Date(1970, 10, 20, 6), y:1.92}]
          },
          { type: 'nitrate',
            values:
             [{ x:2, date:new Date(1970, 9, 29, 2), y:1.3},
              { x:3, date:new Date(1970, 9, 29, 3), y:1.7},
              { x:4, date:new Date(1970, 9, 29, 6), y:1.92},
              { x:23, date: new Date(1970, 9, 29, 1), y:0},
              ]
          },
          { type: 'Ammo',
             values:
             [{ x:1, date:new Date(1970, 9, 29, 7), y:4},
              { x:5, date:new Date(1970, 9, 29, 12), y:4.92},
              { x:10, date:new Date(1970, 9, 29, 15), y:3.92}]
          }
       ]
    },
    { name: 'system_5678',
      measurement:
      [
          { type: 'pH',
            values:
             [{ 'x' : 0, 'y' : 6.0, date: new Date(1970, 9, 29, 7) },
              { 'x' : 1, 'y' : 9.0, date: new Date(1970, 10, 29, 7) },
              { 'x' : 2, 'y' : 17.2, date: new Date(1970, 10,15, 7) }]
          },
          { type: 'nitrate',
            values:
             [{ 'x' : 360, 'y' : 6.5, date: new Date(1970, 04,15, 7) },
              { 'x' : 384, 'y' : 6.5, date: new Date(1970, 05,11, 7) }]
          }
       ]
    }
]
