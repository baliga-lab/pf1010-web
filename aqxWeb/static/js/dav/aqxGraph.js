// Constants
var XAXIS = "selectXAxis";
var YAXIS = "selectYAxis";
var XAXISVALUE = "";
var YAXISVALUE = "";
var OPTION = 'option';
var CHART = "";

window.onload = function () {
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
        if(!(_.isEqual(XAXISVALUE, YAXISVALUE))) {
            CHART.options.title.text = "Last DataPoint Updated";
            // To add new system to graph
            if(_.isEqual(YAXISVALUE, "Add")) {
                CHART.options.data.push(egData);
            }
            CHART.render();
        } else if (_.isEqual(XAXISVALUE, YAXISVALUE)) {
            alert("Please select different values for X and Y");
        }
    }
};

// TODO: Remove these dummy data
var measurement_data_info = ['Nitrate', "Ammo", "Time n date", "Add"];

var egData =
{
      type: "line",
      showInLegend: true, name: 'System - 3',
      dataPoints: [
        { x: new Date(2012, 01, 1), y: 0.5},
        { x: new Date(2012, 01, 4), y: 2.3},
        { x: new Date(2012, 01, 5), y: 0.63}
      ]
};




