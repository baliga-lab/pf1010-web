"use strict";

/*
  This is an intermediary step to remove the horrible redundancy in aqxSystemGraph.js
  and aqxGraph.js while retaining the functionality. Step-by-step we empty out the common
  parts and hopefully end up with a single javascript file for the analytics.
*/

var aqxgraph;
if (!aqxgraph) {
    aqxgraph = {};
}

(function () {
    /* ##################################################################################################################
       CONSTANTS
       ################################################################################################################### */

    aqxgraph.XAXIS = "selectXAxis";
    aqxgraph.XAXIS_TITLE = 'Hours since creation';
    aqxgraph.CHART = "";
    aqxgraph.GRAPH_TYPE = "selectGraphType";
    /*
      Used to display data that was entered by user in the past
      "" - Used to display all the data that user has recorded
      30 - Displays all the data recorded in the past 30 days
      60 - Displays all the data recorded in the past 60 days
      90 - Displays all the data recorded in the past 90 days
    */
    aqxgraph.NUM_ENTRIES_ELEMENT_ID = 'selectNumberOfEntries';
    aqxgraph.SELECTED = 'selected';
    aqxgraph.DEFAULT_Y_TEXT = "Nitrate";
    aqxgraph.DEFAULT_Y_VALUE = aqxgraph.DEFAULT_Y_TEXT.toLowerCase();
    aqxgraph.CHART_TITLE = "System Analyzer";
    aqxgraph.HC_OPTIONS;
    aqxgraph.COLORS = ["lime", "orange", '#f7262f', "lightblue"];
    aqxgraph.DASHSTYLES = ['Solid', 'LongDash', 'ShortDashDot', 'ShortDot', 'LongDashDotDot'];
    aqxgraph.MARKERTYPES = ["circle", "square", "diamond", "triangle", "triangle-down"];
    aqxgraph.DANGER = 'danger';
    aqxgraph.MAXSELECTIONS = 4;
    aqxgraph.BACKGROUND = {
        linearGradient: { x1: 0, y1: 0, x2: 1, y2: 1 },
        stops: [ [0, '#2a2a2b'], [1, '#3e3e40'] ]
    };

    // These are in aqxGraph.js but not in aqxSystemGraph.js ...
    var OVERLAY = true;
    var PRE_ESTABLISHED = 100;
    var ESTABLISHED = 200;
    var SPACE = ' ';
    var GMT = 'GMT';
    // ---------------------

}());
