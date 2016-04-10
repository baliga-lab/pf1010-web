/*(function () {
 $("#slides").slidesjs({
 width: 1600,
 height: 900,
 navigation: false,
 pagination: false,
 play: {
 active: false,
 // [boolean] Generate the play and stop buttons.
 // You cannot use your own buttons. Sorry.
 effect: "slide",
 // [string] Can be either "slide" or "fade".
 interval: 4000,
 // [number] Time spent on each slide in milliseconds.
 auto: true,
 // [boolean] Start playing the slideshow on load.
 swap: false,
 // [boolean] show/hide stop and play buttons
 pauseOnHover: false,
 // [boolean] pause a playing slideshow on hover
 restartDelay: 2500
 // [number] restart delay on inactive slideshow
 }
 });
 })();*/

// SYSTEM TABS
function activateSectionGeneric(section, panelSelectors, liSelectors) {
    var selector = "#" + section + "-panel";
    for (var i = 0; i < panelSelectors.length; i++) {
        if (panelSelectors[i] !== selector) {
            $(panelSelectors[i]).removeClass('hidden');
            $(panelSelectors[i]).addClass('hidden');
        }
    }
    $(selector).removeClass('hidden');
    selector = "#" + section + "-li";
    for (var i = 0; i < liSelectors.length; i++) {
        $(liSelectors[i]).removeClass('active');
    }
    $(selector).addClass('active');
}

function activateSection(section) {
    var panelSelectors = ["#overview-panel", "#analytics-panel", "#measurement-panel", "#annotation-panel", "#notes-panel", "#import-panel", "#connect-panel"];
    var liSelectors = ["#overview-li", "#analytics-li", "#measurement-li", "#annotation-li", "#notes-li", "#import-li", "#connect-li"];
    activateSectionGeneric(section, panelSelectors, liSelectors);
}

$('#analytics-link').click(function () {
    activateSection("analytics");
});
$('#overview-link').click(function () {
    activateSection("overview");
});
$('#measurement-link').click(function () {
    activateSection("measurement");
});
$('#annotation-link').click(function () {
    activateSection("annotation");
});
$('#notes-link').click(function () {
    activateSection("notes");
});
$('#connect-link').click(function () {
    activateSection("connect");
});
$('#import-link').click(function () {
    activateSection("import");
});

// MEASUREMENTS TABS
function activateTab(section) {
    var panelSelectors = ["#dio-panel", "#temp-panel", "#light-panel", "#nh4-panel", "#no3-panel", "#no2-panel", "#ph-panel", "#cl-panel", "#hard-panel", "#alk-panel"];
    var liSelectors = ["#dio-li", "#temp-li", "#light-li", "#nh4-li", "#no3-li", "#no2-li", "#ph-li", "#cl-li", "#hard-li", "#alk-li"];
    activateSectionGeneric(section, panelSelectors, liSelectors);
}

$('#dio-link').click(function () {
    activateTab("dio");
});
$('#temp-link').click(function () {
    activateTab("temp");
});
$('#light-link').click(function () {
    activateTab("light");
});
$('#nh4-link').click(function () {
    activateTab("nh4");
});
$('#no3-link').click(function () {
    activateTab("no3");
});
$('#no2-link').click(function () {
    activateTab("no2");
});
$('#ph-link').click(function () {
    activateTab("ph");
});
$('#cl-link').click(function () {
    activateTab("cl");
});
$('#hard-link').click(function () {
    activateTab("hard");
});
$('#alk-link').click(function () {
    activateTab("alk");
});
