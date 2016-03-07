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
        //[
        //    {
        //        type: "line",
        //        showInLegend: true, name : 'System - 24',
        //        dataPoints: [
        //            { x: 23, date: new Date(1970, 9, 29, 1), y:0},
        //            { x:1, date:new Date(1970, 9, 29, 7), y:4},
        //            { x:2, date:new Date(1970, 9, 29, 2), y:1.3},
        //            { x:3, date:new Date(1970, 9, 29, 3), y:1.7},
        //            { x:4, date:new Date(1970, 9, 29, 6), y:1.92},
        //            { x:5, date:new Date(1970, 9, 29, 12), y:4.92},
        //            { x:10, date:new Date(1970, 9, 29, 15), y:3.92},
        //            { x:6, date:new Date(1970, 10, 9, 2), y:0.4},
        //            { x:11, date:new Date(1970, 11, 1), y:0.25},
        //            { x:35, date:new Date(1971, 0, 1), y:1.66},
        //            { x:40, date:new Date(1971, 0, 10), y:1.8},
        //            { x:22, date:new Date(1971, 1, 19), y:1.76},
        //            { x:29, date:new Date(1971, 2, 25), y:2.62},
        //            { x:50, date:new Date(1971, 3, 19), y:2.41},
        //            { x:25, date:new Date(1971, 3, 30), y:2.05},
        //            { x:48, date:new Date(1971, 4, 14), y:1.7}
        //        ]
        //    },
        //    {
        //        type: "line",
        //        showInLegend: true, name : 'System - 22',
        //        dataPoints: [
        //            { x:23, date: new Date(1970, 9, 29, 1), y:0},
        //            { x:1, date:new Date(1970, 9, 29, 7), y:4},
        //            { x:2, date:new Date(1970, 9, 29, 2), y:1.3},
        //            { x:3, date:new Date(1970, 9, 29, 3), y:1.7},
        //            { x:4, date:new Date(1970, 9, 29, 6), y:1.92},
        //            { x:5, date:new Date(1970, 9, 29, 12), y:4.92},
        //            { x:10, date:new Date(1970, 9, 29, 15), y:3.92},
        //            { x:6, date:new Date(1970, 10, 9, 2), y:0.4},
        //            { x:11, date:new Date(1970, 11, 1), y:0.25},
        //            { x:35, date:new Date(1971, 0, 1), y:1.66},
        //            { x:40, date:new Date(1971, 0, 10), y:1.8},
        //            { x:22, date:new Date(1971, 1, 19), y:1.76},
        //            { x:29, date:new Date(1971, 2, 25), y:2.62},
        //            { x:50, date:new Date(1971, 3, 19), y:2.41},
        //            { x:25, date:new Date(1971, 3, 30), y:2.05},
        //            { x:48, date:new Date(1971, 4, 14), y:1.7}
        //        ]
        //    }
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

var populateDropdown = function(elementId, measurement_data_object){
    var select = document.getElementById(elementId);
    _.each(measurement_data_object, function(measurement_type){
        var el = document.createElement(OPTION);
        el.textContent = measurement_type;
        el.value = measurement_type;
        select.appendChild(el);
    });
};

//var plotGraph = function(xAxisVal) {
//    console.log(xAxisVal + "  ");
//    //  Enter only if both the dropdowns are not null
//    //if(!(_.isEmpty(XAXISVALUE) && _.isEmpty(YAXISVALUE))) {
//    //    counter  = counter + 15;
//    //    console.log(counter);
//    //    if(!(_.isEqual(XAXISVALUE, YAXISVALUE))) {
//    //        CHART.options.title.text = "Last DataPoint Updated";
//    //        // To add new system to graph
//    //        if(_.isEqual(YAXISVALUE, "Time n date")) {
//    //            CHART.options.data.push(egData);
//    //        }
//    //        if(_.isEqual(YAXISVALUE, "Nitrate")) {
//    //            CHART.options.data.push(NitroData);
//    //            console.log(dataPointWrapper(metadataFromDB, 'system_1234', 'ph'));
//    //        }
//    //        if(_.isEqual(YAXISVALUE, "Ammo")) {
//    //            CHART.options.data.push(AmmoData);
//    //        }
//    //        CHART.render();
//    //    } else if (_.isEqual(XAXISVALUE, YAXISVALUE)) {
//    //        alert("Please select different values for X and Y");
//    //    }
//    //}
//    if(!(_.isEmpty(XAXISVALUE))) {
//        console.log(counter);
//        if(!(_.isEqual(XAXISVALUE))) {
//            CHART.options.title.text = "Last DataPoint Updated";
//            // To add new system to graph
//            if(_.isEqual(XAXISVALUE, "Time n date")) {
//                CHART.options.data.push(egData);
//            }
//            if(_.isEqual(XAXISVALUE, "Nitrate")) {
//                CHART.options.data.push(NitroData);
//                console.log(dataPointWrapper(metadataFromDB, 'system_1234', 'pH'));
//            }
//            if(_.isEqual(XAXISVALUE, "Ammo")) {
//                CHART.options.data.push(AmmoData);
//            }
//            CHART.render();
//        }
//    }
//};

// TODO: Remove these dummy data
var measurement_data_info = ['Nitrate', "Ammo", "Time n date"];

var egData =
{
    type: "line",
    showInLegend: true, name: "System - Time n Date" + Math.random(),
    dataPoints: [
        { x: new Date(2012, 01, 11), y: Math.random() * 0.5},
        { x: new Date(2012, 04, 22), y: Math.random() * 2.3},
        { x: new Date(2012, 06, 30), y: Math.random() * 0.63}
    ]
};


var counter = 10;

var hcData = {
    name: 'System -Time n Date',
    data: [
        [(Math.floor(Math.random() * 6) + 1 ) * counter, (Math.floor(Math.random() * 6) + 40 ) * 1.4],
        [(Math.floor(Math.random() * 40) + 2 ) * counter, (Math.floor(Math.random() * 7) + 1 )],
        [(Math.floor(Math.random() * 90) + 3 ) + counter, (Math.floor(Math.random() * 2) + 1 ) * 1.5],
    ]
};


var hcNitro = {
    name: 'System Nitro',
    data: [[110,12.4],[127, 11 ],[125, 9],]
};

var NitroData =
{
    type: "line",
    showInLegend: true, name: "System - Nitro" + Math.random(),
    dataPoints: [
        { x: new Date(2012, 01, 3), y: Math.random() * 0.5},
        { x: new Date(2012, 12, 4), y: Math.random() * 2.3},
        { x: new Date(2012, 07, 10), y: Math.random() * 0.63}
    ]
};

var hcAmmo = {
    name: 'System Ammo',
    data: [[120,22.4],[237, 31 ],[225, 49],]
};

var AmmoData =
{
    type: "line",
    showInLegend: true, name: "System - Ammo" + Math.random(),
    dataPoints: [
        { x: new Date(2012, 06, 13), y: Math.random() * 0.5},
        { x: new Date(2012, 12, 24), y: Math.random() * 2.3},
        { x: new Date(2012, 07, 10), y: Math.random() * 0.63}
    ]
};
var metadataFromDB = [
    { name: 'system_1234' ,
        measurement: [
            { type: 'pH',
                values:
                    [{ 'x' : 0, 'y' : 7.0, date: new Date('03:03:16:00') },
                        { 'x' : 1, 'y' : 11.0, date: new Date('03:03:16:01')},
                        { 'x' : 2, 'y' : 9.2, date: new Date('03:03:16:02') }]
            },
            { type: 'nitrate',
                values: 'nitrate'
                    [{ 'x' : 360, 'y' : 6.5, date: new Date('03:01:16:12')},
                { 'x' : 384, 'y' : 6.5, date: new Date('03:02:16:12') }]
            }
        ]
    },
    { name: 'system_5678',
        measurement:
            [
                { type: 'pH',
                    values:
                        [{ 'x' : 0, 'y' : 6.0, date: new Date('03:03:16:00') },
                            { 'x' : 1, 'y' : 9.0, date: new Date('03:03:16:01') },
                            { 'x' : 2, 'y' : 17.2, date: new Date('03:03:16:02') }]
                },
                { type: 'nitrate',
                    values:
                        [{ 'x' : 360, 'y' : 6.5, date: new Date('03:01:16:12') },
                            { 'x' : 384, 'y' : 6.5, date: new Date('03:02:16:12') }]
                }
            ]
    }
]

var dataPointWrapper = function(metaData, systemUID, measurementType) {
    _.each(metaData, function(system) {
        if(_.isEqual(system.name, systemUID)) {
            var measurements = system.measurement;
            _.each(measurements, function(measurement) {
                if(_.isEqual(measurement.type, measurementType)) {
                    return measurement.values;
                }
            })
            //return system.measurement[measurementType];
        }
    });
};

// Sort datapoints based on the abs hours
//

