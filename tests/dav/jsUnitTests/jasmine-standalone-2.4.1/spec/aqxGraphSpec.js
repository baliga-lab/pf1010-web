var data = {aqx_technique_name : "error"};
var statusID = "Established"

var systemName = "Test123";
var dataPoints = [];
var graphType = "scatter";
var id = "123";
var linkedTo = "1";
var color = "blue";
var yAxis = "ppm";
var dashStyle = "dots";
var markerType = "dot";
var yType = "Nitrate";
var opposite = true;
var unitLabel = "celcius";
var units = "celcius";


var series = ({
    name: 'Test123,Nitrate',
    type: 'scatter',
    data: [],
    color: 'blue',
    id: '123',
    yAxis: 'ppm',
    dashStyle: 'dots',
    marker: { symbol: 'dot' } });

var yOutput = ({
        title:
        {
            text: yType,
            style: {color: color}
        },
        labels:
        {
            format: '{value} ' + unitLabel,
            style: {color: color}
        },
        showEmpty: false,
        lineWidth: 1,
        tickWidth: 1,
        gridLineWidth: 1,
        opposite: opposite,
        gridLineColor: '#707073',
        lineColor: '#707073',
        minorGridLineColor: '#505053',
        tickColor: '#707073'
});


describe("Functions for aqxGraph", function() {

    it("should display an error response", function()  {
        expect(processAJAXResponse(data, statusID)).toBe();
    });

    it("should return a JSON object", function()  {
        expect(getDataPoints(systemName, dataPoints, graphType, id, linkedTo, color, yAxis, dashStyle, markerType, yType)).not.toBe(null);
    });


    it("should create a yAxis", function() {
        expect(createYAxis(yType, color, opposite, units)).not.toBe(null);
    });

});

