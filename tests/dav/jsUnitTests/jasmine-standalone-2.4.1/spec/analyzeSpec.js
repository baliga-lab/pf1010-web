/* ##################################################################################################################
 CONSTANTS
 ################################################################################################################### */

var CHART_TITLE = "System Analyzer";
var poopChart;
var mockChart;

describe("Analysis graph page", function() {
    console.log("before mockCharts");
    beforeEach(function(done) {
        poopChart = new Highcharts.chart({
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
            // TODO: Maybe init units first then we can cut out a line here.
            formatter: function() {
                var tooltipInfo = this.series.name.split(",");
                var yVal = tooltipInfo[1];
                var units = measurement_types_and_info[yVal]['unit'];
                units = (units) ? units : "";
                units = (_.isEqual(units, "celsius")) ? "°C" : units;
                yVal = yVal.charAt(0).toUpperCase() + yVal.slice(1);
                var datetime = this.point.date.split(" ");
                return '<b>' + tooltipInfo[0] + '</b>' +
                    '<br><p>' + yVal + ": " + this.y + ' ' + units + '</p>' +
                    '<br><p>Hours in cycle: ' + this.x + '</p>' +
                    '<br><p>Measured on: ' + datetime[0] + '</p>' +
                    '<br><p>At time: ' + datetime[1] +'</p>';
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
            yAxis: [],
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
        });
        mockChart = new Highcharts.chart({
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
            // TODO: Maybe init units first then we can cut out a line here.
                formatter: function() {
                    var tooltipInfo = this.series.name.split(",");
                    var yVal = tooltipInfo[1];
                    var units = measurement_types_and_info[yVal]['unit'];
                    units = (units) ? units : "";
                    units = (_.isEqual(units, "celsius")) ? "°C" : units;
                    yVal = yVal.charAt(0).toUpperCase() + yVal.slice(1);
                    var datetime = this.point.date.split(" ");
                    return '<b>' + tooltipInfo[0] + '</b>' +
                        '<br><p>' + yVal + ": " + this.y + ' ' + units + '</p>' +
                        '<br><p>Hours in cycle: ' + this.x + '</p>' +
                        '<br><p>Measured on: ' + datetime[0] + '</p>' +
                        '<br><p>At time: ' + datetime[1] +'</p>';
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
            yAxis: [],
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
        });
        done();
        console.log("between mock and poop");
    });
    //beforeEach(function(done) {
    console.log("right before calling expect");
    it("should clear out the old graph data", function()  {
        expect(clearOldGraphValues(mockChart)).toBe(mockChart);
        //done();
    });
    console.log("after mockCharts");
});
