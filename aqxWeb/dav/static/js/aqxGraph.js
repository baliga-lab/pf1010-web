// Constants
var XAXIS = "selectXAxis";
var YAXIS = "selectYAxis";
var XAXISVALUE = "";
var YAXISVALUE = "";
var OPTION = 'option';
var CHART = "";
var HC = "";
var HC_OPTIONS;
var data


window.onload = function () {
    //data = request.get_json();
    CHART = new CanvasJS.Chart("analyzeContainer", {
        title:{
          text: "My First Chart in CanvasJS"
        },
        data:
        [
            {
              // Change type to "doughnut", "line", "splineArea", etc.
              type: "line",
              showInLegend: true, name : 'System - 1',
              dataPoints: [
                { x: new Date(2012, 01, 1), y: 0.4},
                { x: new Date(2012, 01, 3), y: 0.3},
                { x: new Date(2012, 01, 5), y: 0.33}
              ]
            },
            {
              type: "line",
              showInLegend: true, name : 'System - 2',
              dataPoints: [
                { x: new Date(2012, 01, 1), y: 0.14},
                { x: new Date(2012, 01, 3), y: 0.32},
                { x: new Date(2012, 01, 5), y: 0.53}
              ]
            }
        ]
    });
    CHART.render();

    HC_OPTIONS = {
        chart: {
            renderTo: 'hcContainer',
            type: 'line'
        },
        xAxis: {
            minPadding: 0.05,
            maxPadding: 0.05
        },
        series: [{
            name: 'System 1',
            data: [
                [0, 29.9],
                [1, 71.5],
                [3, 106.4]
            ]
        }]
    };
    HC = new Highcharts.Chart(HC_OPTIONS);

};


$(function() {

//  Populate X and Y axis dropdowns
    populateDropdown(XAXIS, measurement_data_info);
    populateDropdown(YAXIS, measurement_data_info);

//  Get selected values from dropdown
    $("#" +XAXIS).change(function () {
        XAXISVALUE  = $('option:selected', this).text();
        plotGraph(XAXISVALUE,YAXISVALUE);
    });

    $("#" +YAXIS).change(function () {
        YAXISVALUE  = $('option:selected', this).text();
        plotGraph(XAXISVALUE,YAXISVALUE);
    });
});

var populateDropdown = function(elementId, measurement_data_object){
    var select = document.getElementById(elementId);
    _.each(measurement_data_object, function(measurement_type){
        var el = document.createElement(OPTION);
        el.textContent = measurement_type;
        el.value = measurement_type;
        select.appendChild(el);
    });
};

var plotGraph = function(xAxisVal, yAxisVal) {
    console.log(xAxisVal + "  " + yAxisVal);
    //  Enter only if both the dropdowns are not null
    if(!(_.isEmpty(XAXISVALUE) && _.isEmpty(YAXISVALUE))) {
        counter  = counter + 15;
        console.log(counter);
        if(!(_.isEqual(XAXISVALUE, YAXISVALUE))) {
            CHART.options.title.text = "Last DataPoint Updated";
            // To add new system to graph
            if(_.isEqual(YAXISVALUE, "Time n date")) {
                CHART.options.data.push(egData);
                HC.addSeries(hcData);
            }
            if(_.isEqual(YAXISVALUE, "Nitrate")) {
                CHART.options.data.push(NitroData);
                HC.addSeries(hcNitro);
            }
            if(_.isEqual(YAXISVALUE, "Ammo")) {
                CHART.options.data.push(AmmoData);
                HC.addSeries(hcAmmo);
            }
            HC.redraw();
            CHART.render();
        } else if (_.isEqual(XAXISVALUE, YAXISVALUE)) {
            alert("Please select different values for X and Y");
        }
    }
};

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



