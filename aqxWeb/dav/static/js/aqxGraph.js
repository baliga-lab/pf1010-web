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
var CHART_TITLE = "";
var HC_OPTIONS;
var COLORS = ["lime", "orange", '#f7262f', "lightblue"];
var DASHSTYLES = ['Solid', 'LongDash', 'ShortDashDot', 'ShortDot', 'LongDashDotDot'];
var MARKERTYPES = ["circle", "square", "diamond", "triangle", "triangle-down"];



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
// TODO: Make more efficient. Just pass an iterator that determines yAxis, dashStyle, marker.symbol, and color.
var getDataPoints = function(systemName, dataPoints, color, graphType, id, linkedTo, yAxis, dashStyle, markerType, yType) {
    series = { name: systemName + ',' + yType,
        type: graphType,
        data: dataPoints,
        color: color,
        id: id,
        yAxis: yAxis,
        dashStyle: dashStyle,
        marker: {symbol: markerType}
    };
    if(linkedTo) {
        series.linkedTo = id;
    }
    return series;
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

    var dataPointsList = [];
    // Every system should be represented by unique color
    // Each measurementType should have a unique marker type

    var axes = [false, false, false, false];
    _.each(systems_and_measurements, function(system, j){
        var measurements = system.measurement;
        // Used to link measurements to system
        var linkedTo = false;
        var i = 0;
        _.each(yTypeList, function(yType) {
            _.each(measurements, function(measurement){
                if (_.isEqual(measurement.type.toLowerCase(), yType.toLowerCase())) {
                    var systemId = system.system_uid;
                    if (measurement.values.length > 0){
                        if (!axes[i]) {
                            chart.addAxis(createYAxis(yType, i, COLORS[i], measurement_types_and_info[yType]['unit']));
                            axes[i] = true;
                        }
                        dataPointsList.push(
                            getDataPoints(system.name, measurement.values, COLORS[i],
                                graphType, systemId,linkedTo, i, DASHSTYLES[j], MARKERTYPES[j], yType));
                        linkedTo = true;
                        i += 1;
                    }
                    else{
                        console.log("No measurements for " + yType);
                    }
                }
            });
        });
    });
    return dataPointsList;
};


/**
 *
 * @param yType
 * @param numAxes
 * @param color - index number that is mapped to COLORS[] array
 * @returns {{title: {text: *}, labels: {format: string, style: {color: *}}, opposite: boolean}}
 */
var createYAxis = function(yType, numAxes, color, units){
    return { // Primary yAxis
        title:
        {
            text: yType,
            style: {color: color}
        },
        labels:
        {
            format: '{value} ' + units,
            style: {color: color }
        },
        showEmpty: false,
        lineWidth: 1,
        tickWidth: 1,
        gridLineWidth: 1,
        opposite: !(numAxes % 2 === 0),
        gridLineColor: '#707073',
        lineColor: '#707073',
        minorGridLineColor: '#505053',
        tickColor: '#707073',
    }

};

/**
 *
 * @param chart - A CanvasJS chart
 * @param xType - X-axis value chosen from dropdown
 * @param yTypeList - List of y-axis values selected from the checklist
 * @param graphType - The graph type chosen from dropdown
 */
var updateChartDataPointsHC = function(chart, xType, yTypeList, graphType){
    var activeMeasurements = getAllActiveMeasurements();
    var measurementsToFetch = _.difference(yTypeList, activeMeasurements);
    var measurementIDList = [];
    _.each(measurementsToFetch, function(measurement){
        measurementIDList.push(measurement_types_and_info[measurement]['id']);
    });
    chart = clearOldGraphValues(chart);
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
    }
    chart.xAxis[0].setTitle({ text: "hours since creation" });
    var newDataSeries = getDataPointsForPlotHC(chart, xType, yTypeList, graphType);
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
 *
 */
var setDefaultYAxis = function() {
    $(".js-example-basic-multiple").select2();
    $(".js-example-basic-multiple").val(DEFAULT_Y_VALUE).trigger("change");
};


/**
 *
 */
var drawChart = function(){
    var graphType = document.getElementById(GRAPH_TYPE).value;
    var xType = document.getElementById(XAXIS).value;

    // Get measurement types to display on the y-axis
    var yTypes = $(".js-example-basic-multiple").select2().val();

    // Generate a data Series for each y-value type, and assign them all to the CHART
    updateChartDataPointsHC(CHART, xType, yTypes, graphType).redraw();
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

    $.fn.select2.defaults.set("maximumSelectionLength", 4);

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
            zoomType: 'xy',
            backgroundColor: {
                linearGradient: { x1: 0, y1: 0, x2: 1, y2: 1 },
                stops: [
                    [0, '#2a2a2b'],
                    [1, '#3e3e40']
                ]
            },
            plotBorderColor: '#606063'
        },
        title: {
            text: CHART_TITLE
        },
        credits: {
            style: {
                color: '#666'
            }
        },
        tooltip: {
            formatter: function() {
                var tooltipInfo = this.series.name.split(",");
                var yVal = tooltipInfo[1];
                var yValCap = yVal.charAt(0).toUpperCase() + yVal.slice(1);
                var datetime = this.point.date.split(" ");
                //console.log(this.point.date);
                return '<b>' + tooltipInfo[0] + '</b>' +
                    '<br><p>' + yValCap + ": " + this.y + ' ' + measurement_types_and_info[yVal]['unit'] + '</p>' +
                    '<br><p>Hours in cycle: ' + this.x + '</p>' +
                    '<br><p>Measured on: ' + datetime[0] + '</p>' +
                    '<br><p>At time: ' + datetime[1] +'</p>';
                //return 'The value at <b>' + this.x + '</b> hour was <b>' + this.y + '</b>, in series '+ this.series.name;
            },
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

Highcharts.theme = {
    colors: ["#2b908f", "#90ee7e", "#f45b5b", "#7798BF", "#aaeeee", "#ff0066", "#eeaaee",
        "#55BF3B", "#DF5353", "#7798BF", "#aaeeee"],
    chart: {
        backgroundColor: {
            linearGradient: { x1: 0, y1: 0, x2: 1, y2: 1 },
            stops: [
                [0, '#2a2a2b'],
                [1, '#3e3e40']
            ]
        },
        plotBorderColor: '#606063'
    },
    title: {
        style: {
            color: '#E0E0E3',
            textTransform: 'uppercase',
            fontSize: '20px'
        }
    },
    subtitle: {
        style: {
            color: '#E0E0E3',
            textTransform: 'uppercase'
        }
    },
    xAxis: {
        gridLineColor: '#707073',
        labels: {
            style: {
                color: '#E0E0E3'
            }
        },
        lineColor: '#707073',
        minorGridLineColor: '#505053',
        tickColor: '#707073',
        title: {
            style: {
                color: '#A0A0A3'

            }
        }
    },
    tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
        style: {
            color: '#F0F0F0'
        }
    },
    plotOptions: {
        series: {
            dataLabels: {
                color: '#B0B0B3'
            },
            marker: {
                lineColor: '#333'
            }
        },
        boxplot: {
            fillColor: '#505053'
        },
        candlestick: {
            lineColor: 'white'
        },
        errorbar: {
            color: 'white'
        }
    },
    legend: {
        itemStyle: {
            color: '#E0E0E3'
        },
        itemHoverStyle: {
            color: '#FFF'
        },
        itemHiddenStyle: {
            color: '#606063'
        }
    },
    credits: {
        style: {
            color: '#666'
        }
    },
    labels: {
        style: {
            color: '#707073'
        }
    },

    drilldown: {
        activeAxisLabelStyle: {
            color: '#F0F0F3'
        },
        activeDataLabelStyle: {
            color: '#F0F0F3'
        }
    },

    navigation: {
        buttonOptions: {
            symbolStroke: '#DDDDDD',
            theme: {
                fill: '#505053'
            }
        }
    },

    // scroll charts
    rangeSelector: {
        buttonTheme: {
            fill: '#505053',
            stroke: '#000000',
            style: {
                color: '#CCC'
            },
            states: {
                hover: {
                    fill: '#707073',
                    stroke: '#000000',
                    style: {
                        color: 'white'
                    }
                },
                select: {
                    fill: '#000003',
                    stroke: '#000000',
                    style: {
                        color: 'white'
                    }
                }
            }
        },
        inputBoxBorderColor: '#505053',
        inputStyle: {
            backgroundColor: '#333',
            color: 'silver'
        },
        labelStyle: {
            color: 'silver'
        }
    },

    navigator: {
        handles: {
            backgroundColor: '#666',
            borderColor: '#AAA'
        },
        outlineColor: '#CCC',
        maskFill: 'rgba(255,255,255,0.1)',
        series: {
            color: '#7798BF',
            lineColor: '#A6C7ED'
        },
        xAxis: {
            gridLineColor: '#505053'
        }
    },

    scrollbar: {
        barBackgroundColor: '#808083',
        barBorderColor: '#808083',
        buttonArrowColor: '#CCC',
        buttonBackgroundColor: '#606063',
        buttonBorderColor: '#606063',
        rifleColor: '#FFF',
        trackBackgroundColor: '#404043',
        trackBorderColor: '#404043'
    },

    // special colors for some of the
    legendBackgroundColor: 'rgba(0, 0, 0, 0.5)',
    background2: '#505053',
    dataLabelsColor: '#B0B0B3',
    textColor: '#C0C0C0',
    contrastTextColor: '#F0F0F3',
    maskColor: 'rgba(255,255,255,0.3)'
};