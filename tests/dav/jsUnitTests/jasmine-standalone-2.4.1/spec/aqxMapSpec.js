
var alertText = "Notifying the user";
var type = "Danger";
var latLng = new google.maps.LatLng("43", "-122");
var marker = new google.maps.Marker({
    title: "Testing123",
    position: latLng,
    map: MAP,
    content: "",
    icon: DEFAULT_ICON,
    zIndex: google.maps.Marker.MIN_ZINDEX
});

var system = {aqx_technique_name : "Nutrient Film Technique (NFT)",
    organism_name : "Goldfish",
    crop_name : "Lettuce",
    growbed_media : "Clay Pebbles",
    status : "200"
};

var systemID = "0012345678911011121314151617181920";
var ddAqxTech = "Nutrient Film Technique (NFT)";
var ddAqxOrg = "Goldfish";
var ddAqxCrop = "Lettuce";
var ddAqxMedia = "Clay Pebbles";
var ddStatus = "100";




describe("Functions for aqxMap", function() {

    it("should display a notification message to the users", function()  {
        expect(getAlertHTMLString(alertText, type)).toBe('<div class="alert alert-Danger"><a class="close" data-dismiss="alert">×</a><span>Notifying the user</span></div>');
    });

    it("should test if the marker is not starred", function() {
        expect(markerIsStarred(marker)).toBeFalsy();
    });

    it("should test if the marker is starred", function() {
        marker.setIcon(SELECTED_ICON);
        expect(markerIsStarred(marker)).toBeTruthy();
    });

    it("should build content string", function() {
        expect(buildContentString(system)).not.toEqual(null);
    });

    it("should compare a system's metadata and return false", function () {
        expect(systemMetadataDoesNotMatchesAnyDropdown(system, "Nutrient Film Technique (NFT)", "Goldfish", "Lettuce", "Clay Pebbles", "200")).toBeFalsy();
    });

    it("should compare a system's metadata and return true (because it doesn't make)", function () {
        expect(systemMetadataDoesNotMatchesAnyDropdown(system, "Nutrient Film Technique (NFT)", "Goldfish", "Lettuce", "Clay Pebbles", "100")).toBeTruthy();
    });

//
//    it("should flip icons for the given system", function(){
//        notify = jasmine.createSpy("getSelectedSystemIds() spy").and.callFake(function() {
//            return systemID;
//        });
//        expect(flipIcons(marker, systemID)).toHaveBeenCalled();
//        });
});



