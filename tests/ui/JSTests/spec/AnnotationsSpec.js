describe("Annotations", function () {

    describe("when pH is selected from dropdown", function () {
        it("should display Added Base & Added Acid options", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();

            // select ph from dropdown
            $("#mySelect").val("ph");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType2").is(":visible")).toBe(true);

            // check if Added Base and Added Acid are shown
            expect($("#otherType2 span label span").length).toBe(2);
            expect($("#otherType2 span label span")[0].innerHTML).toBe("Added Base");
            expect($("#otherType2 span label span")[1].innerHTML).toBe("Added Acid");

        });
    });

    describe("when Added Base or Added Acid is selected", function () {
        it("should set accurate annotation ids", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();

            // select ph from dropdown
            $("#mySelect").val("ph");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType2").is(":visible")).toBe(true);
            // Click Added Base and check for annotation ID
            $("input[name=seg2][value=Low][type=radio]").click();
            expect($('#number').val()).toBe("2");

            // Click Added Acid and check for annotation ID
            $("input[name=seg2][value=High][type=radio]").click();
            expect($('#number').val()).toBe("3");
        });

        it("should display accurate information associated to the selection", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();

            // select ph from dropdown
            $("#mySelect").val("ph");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType2").is(":visible")).toBe(true);
            // Click Added Base and check for annotation ID

           $("input[name=seg2][value=Low][type=radio]").click();
            expect($('#phLowInfo').is(":visible")).toBe(true);
            expect($('#phHighInfo').is(":visible")).toBe(false);

           $("input[name=seg2][value=High][type=radio]").click();
            expect($('#phHighInfo').is(":visible")).toBe(true);
            expect($('#phLowInfo').is(":visible")).toBe(false);

        });
    });



    describe("when Harvest is selected from dropdown", function () {
        it("should display Plant Harvested & Fish Harvested options", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();

            // select harvest from dropdown
            $("#mySelect").val("harvest");
            $("#mySelect").trigger("change");
            //check if radio buttons are visible
            expect($("#otherType4").is(":visible")).toBe(true);

            // check if Plant Harvested and Fish Harvested are shown
            expect($("#otherType4 span label span").length).toBe(2);
            expect($("#otherType4 span label span")[0].innerHTML).toBe("Plant Harvested");
            expect($("#otherType4 span label span")[1].innerHTML).toBe("Fish Harvested");
        });
    });


    describe("when Plant Harvested or Fish Harvested is selected", function () {
        it("should set accurate annotation ids", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();

            // select harvest from dropdown
            $("#mySelect").val("harvest");
            $("#mySelect").trigger("change");
            //check if radio buttons are visible
            expect($("#otherType4").is(":visible")).toBe(true);

            // Click harvest and check for annotation ID
            $("input[name=seg4][value=harvestPlant][type=radio]").click()
            expect($('#number').val()).toBe("4");

            // Click Added Acid and check for annotation ID
            $("input[name=seg4][value=harvestFish][type=radio]").click()
            expect($('#number').val()).toBe("5");
        });

        it("should display accurate information associated to the selection", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();

            // select harvest from dropdown
            $("#mySelect").val("harvest");
            $("#mySelect").trigger("change");
            //check if radio buttons are visible
            expect($("#otherType4").is(":visible")).toBe(true);

            // Click harvest and check for annotation ID
            $("input[name=seg4][value=harvestPlant][type=radio]").click();
            expect($('#harvestPlantInfo').is(":visible")).toBe(true);
            expect($('#harvestFishInfo').is(":visible")).toBe(false);

            $("input[name=seg4][value=harvestFish][type=radio]").click();
            expect($('#harvestFishInfo').is(":visible")).toBe(true);
            expect($('#harvestPlantInfo').is(":visible")).toBe(false);
        });
    });


    describe("when Fish is selected from dropdown", function () {
        it("should display Fish Added & Fish Remove options", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();
            // select harvest from dropdown
            $("#mySelect").val("fish");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType1").is(":visible")).toBe(true);
            //check if Fish Added and Fish Removed are shown
            expect($("#otherType1 span label span").length).toBe(2);
            expect($("#otherType1 span label span")[0].innerHTML).toBe("Fish Added")
            expect($("#otherType1 span label span")[1].innerHTML).toBe("Fish Removed")
        });
    });

    describe("when Fish Added or Fish Removed is selected", function () {
        it("should set accurate annotation ids", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();
            // select harvest from dropdown
            $("#mySelect").val("fish");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType1").is(":visible")).toBe(true);

            $("input[name=seg1][value=Add][type=radio]").click();
            expect($('#number').val()).toBe("8");

            // Click fish removed and check for annotation ID
            $("input[name=seg1][value=Remove][type=radio]").click();
            expect($('#number').val()).toBe("9");
        });


         it("should display accurate information associated to the selection", function () {
             loadFixtures("annotations.html");
            Annotations.bindDOMEvents();
            // select harvest from dropdown
            $("#mySelect").val("fish");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType1").is(":visible")).toBe(true);

            $("input[name=seg1][value=Add][type=radio]").click();
            expect($('#fishAddInfo').is(":visible")).toBe(true);
            expect($('#fishRemoveInfo').is(":visible")).toBe(false);

           $("input[name=seg1][value=Remove][type=radio]").click();
            expect($('#fishAddInfo').is(":visible")).toBe(false);
            expect($('#fishRemoveInfo').is(":visible")).toBe(true);

          });
    });

    describe("when Plant is selected from dropdown", function () {
        it("should display Plant Added & Plant Remove options", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();
            // select harvest from dropdown
            $("#mySelect").val("plant");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType1").is(":visible")).toBe(true);
            //check if Plant Added and Plant Removed are shown
            expect($("#otherType1 span label span").length).toBe(2);
            expect($("#otherType1 span label span")[0].innerHTML).toBe("Plant Added")
            expect($("#otherType1 span label span")[1].innerHTML).toBe("Plant Removed")
        });
    });

    describe("when Plant Added or Plant Removed is selected", function () {
        it("should set accurate annotation ids", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();
            // select harvest from dropdown
            $("#mySelect").val("plant");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType1").is(":visible")).toBe(true);

            //check annotation id
            $("input[name=seg1][value=Add][type=radio]").click();
            expect($('#number').val()).toBe("6");

            $("input[name=seg1][value=Remove][type=radio]").click();
            expect($('#number').val()).toBe("7");

        });
    });

    describe("when Bacteria is selected from dropdown", function () {
        it("should display Bacteria Added option", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();
            // select harvest from dropdown
            $("#mySelect").val("bacteria");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType5").is(":visible")).toBe(true);
            // check if Bacteria Added are shown
            expect($("#otherType5 span label span").length).toBe(1);
            expect($("#otherType5 span label span")[0].innerHTML).toBe("Bacteria Added");
        });
    });
    describe("when Bacteria Added is selected", function () {
        it("should set accurate annotation id", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();
            // select harvest from dropdown
            $("#mySelect").val("bacteria");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType5").is(":visible")).toBe(true);

            //check annotation id
            $("input[name=seg5][value=justAdd][type=radio]").click();
            expect($('#number').val()).toBe("10");
        });
    });

    describe("when Clean Tank is selected from dropdown", function () {
        it("should display Clean Tank option", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();
            // select harvest from dropdown
            $("#mySelect").val("cleantank");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType3").is(":visible")).toBe(true);
            // check if Bacteria Added are shown
            expect($("#otherType3 span label span").length).toBe(1);
            expect($("#otherType3 span label span")[0].innerHTML).toBe("Clean Tank");
        });
    });

    describe("when Clean Tank is selected", function () {
        it("should set accurate annotation id", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();
            // select harvest from dropdown
            $("#mySelect").val("cleantank");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType3").is(":visible")).toBe(true);

            $("input[name=seg3][value=Yes][type=radio]").click();
            expect($('#number').val()).toBe("12");
        });
    });


    describe("when Reproduction is selected from dropdown", function () {
        it("should display Yes option", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();
            // select harvest from dropdown
            $("#mySelect").val("reproduction");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType3").is(":visible")).toBe(true);
            // check if Bacteria Added are shown
            expect($("#otherType3 span label span").length).toBe(1);
            expect($("#otherType3 span label span")[0].innerHTML).toBe("Yes");
        });

        it("should display accurate information associated to the selection", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();
            // select harvest from dropdown
            $("#mySelect").val("cleantank");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType3").is(":visible")).toBe(true);

            $("input[name=seg3][value=Yes][type=radio]").click();

            expect($('#cleanTankYesInfo').is(":visible")).toBe(true);

        });
    });


    describe("when (Reproduction) Yes is selected", function () {
        it("should set accurate annotation id", function () {
            loadFixtures("annotations.html");
            Annotations.bindDOMEvents();
            // select harvest from dropdown
            $("#mySelect").val("reproduction");
            $("#mySelect").trigger("change");
            // check if radio buttons are visible
            expect($("#otherType3").is(":visible")).toBe(true);
            $("input[name=seg3][value=Yes][type=radio]").click();
            expect($('#number').val()).toBe("14");

        });
    });

    describe("On clicking submit annotations", function () {

        beforeEach(module('aqx'));

        var $controller;

        beforeEach(inject(function (_$controller_) {
            // The injector unwraps the underscores (_) from around the parameter names when matching
            $controller = _$controller_;
        }));

        it('should submit valid system ID', function () {
            loadFixtures("annotations.html");
            var $scope = {};
            var controller = $controller('AnnotationController', {$scope: $scope});
            expect($("#ID").html()).toBeDefined();
        });
        it('should submit valid Date time', function () {
            loadFixtures("annotations.html");
            var $scope = {};
            var controller = $controller('AnnotationController', {$scope: $scope});
            expect($("#recordedDateAndTime").html()).toBeDefined();
            });
    });
});
