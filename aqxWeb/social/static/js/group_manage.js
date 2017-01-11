"use strict";

var aqx_social;
if (!aqx_social) {
    aqx_social = {};
}

(function () {
    aqx_social.getUserConsent = function() {
        return confirm('Are you sure?');
    };

    $(document).ready(function () {
        $("#manageGroupsTab").tabs();
    });
}());
