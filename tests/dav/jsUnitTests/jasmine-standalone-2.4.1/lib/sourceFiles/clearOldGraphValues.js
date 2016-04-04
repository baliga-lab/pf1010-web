/**
 *
 * @param chart
 * @returns {*}
 */
var clearOldGraphValues = function(chart) {
    console.log(chart);
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


