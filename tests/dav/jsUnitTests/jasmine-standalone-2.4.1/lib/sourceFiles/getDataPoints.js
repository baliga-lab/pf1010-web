/* ##################################################################################################################
 CONSTANTS
 ################################################################################################################### */

var COLORS = ["lime", "orange", '#f7262f', "lightblue"];
var DASHSTYLES = ['Solid', 'LongDash', 'ShortDashDot', 'ShortDot', 'LongDashDotDot'];
var MARKERTYPES = ["circle", "square", "diamond", "triangle", "triangle-down"];


/**
 *
 * @param systemName - name of system
 * @param dataPoints - array of values for graph; [{x:"", y: "", date: "", marker: ""}]
 * @param graphType
 * @param id
 * @param linkedTo - used to group series to a system
 * @param i - The iterator for a measurement
 * @param j - The iterator for a system
 * @param yType - The measurement type name
 * @returns {{name: string, type: *, data: *, color: string, id: *, yAxis: *, dashStyle: string, marker: {symbol: string}}|*}
 */
var getDataPoints = function(systemName, dataPoints, graphType, id, linkedTo, i, j, yType) {
    series = { name: systemName + ',' + yType,
        type: graphType,
        data: dataPoints,
        color: COLORS[i],
        id: id,
        yAxis: i,
        dashStyle: DASHSTYLES[j],
        marker: {symbol: MARKERTYPES[j]}
    };
    if(linkedTo) {
        series.linkedTo = id;
    }
    return series;
};
