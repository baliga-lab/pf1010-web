/* ##################################################################################################################
 CONSTANTS
 ################################################################################################################### */

var COLORS = ["lime", "orange", '#f7262f', "lightblue"];

/**
 *
 * @param yType
 * @param axisNum
 * @param units
 * @returns {{title: {text: *}, labels: {format: string, style: {color: *}}, opposite: boolean}}
 */
var createYAxis = function(yType, axisNum, units){
    var unitLabel = (units) ? units : "";
    unitLabel = (_.isEqual(unitLabel, "celsius")) ? "°C" : unitLabel;
    return { // Primary yAxis
        title:
        {
            text: yType,
            style: {color: COLORS[axisNum]}
        },
        labels:
        {
            format: '{value} ' + unitLabel,
            style: {color: COLORS[axisNum] }
        },
        showEmpty: false,
        lineWidth: 1,
        tickWidth: 1,
        gridLineWidth: 1,
        opposite: !(axisNum % 2 === 0),
        gridLineColor: '#707073',
        lineColor: '#707073',
        minorGridLineColor: '#505053',
        tickColor: '#707073',
    }

};