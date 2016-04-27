/**
 * Using a supplied url, fetch the title, description and image to display
 * as a preview
 *
 * @param url		assume this is a valid url
 */
function getLinkMeta(url) {
    // create the yql query (encoded!) with the url provided
    var q = 'http://query.yahooapis.com/v1/public/yql?q='
        + encodeURIComponent('select * from html where url="' + url + '" and xpath="//title|//head/meta"')
        + '&format=json&callback=?';

    console.log(q);

    $.ajax({
        type: 'GET',
        url: q,
        dataType: 'jsonp',
        success: function (data, textStatus) {
            // make sure we have some data to work with
            if (data) {
                var results = data.query.results;
                console.log(results);

                // will contain only the data we want to display
                var result = {};

                var text;
                var try_image = false;

                if (results && results != null) {

                    // use the html title as the title
                    result.title = results.title;

                    // loop through meta tags to grab the image & description
                    $.each(results.meta, function (key, val) {
                        if (val.content) {
                            // description
                            if (val.name && val.name == 'description') {
                                result.description = val.content;
                            }

                            // og:image (Facebook image) -- starts with http://
                            if ((val.content.substring(0, 7) == 'http://'
                                && val.content.charAt(val.content.length - 4) == '.')
                                || val.property == "og:image") {
                                if (val.content != 'undefined') {
                                    result.img = val.content;
                                    try_image = false;
                                } else {
                                    try_image = true;
                                }
                            }
                        }
                    });
                    if (!try_image) {
                        text = loadLinkData(url, result);

                        $(".links").empty();
                        $(".links").append(text);
                    }
                } else {
                    try_image = true;
                }

                if (try_image) {
                    $("<img>", {
                        src: url,
                        error: function () {
                        },
                        load: function () {
                            result.img = url;
                            text = loadLinkData(url, result);
                            $(".links").empty();
                            $(".links").append(text);
                        }
                    });
                }

            } else {
                console.log("Sorry, can't scrape anything from that url.", 'error');
            }
        }
    });
}
 /**
 * Using a supplied url, fetch the title, description and image to display
 * as a preview
 *
 * @param url		assume this is a valid url
  *       result    the collected result from meta
 */
function loadLinkData(url, result) {
     // build output
    var text = "<div class='row link_preview'>";
    // link title
    if (result.title) {
        text += "<h3>" + result.title  + "</h3>";
        text += "<input type='hidden' name='link_title' value='" + result.title + "'/>";
    }
    // link url
    //text += "<div class='url'><em><a href='" + url + "' target='_blank'>" + url + "</a></em></div>";
    text += "<input type='hidden' name='link' value='" + url + "'/>";
    if (result.img) {
        text += "<img src='" + result.img + "' class='thumb'/>";
        text += "<input type='hidden' name='link_img' value='" + result.img + "'/>";
    }
    // link description
    if (result.description) {
        text += "<p>" + result.description + "</p>";
        text += "<input type='hidden' name='link_description' value='" + result.description + "'/>";
    }
    text += "</div>";
    return text;
}

$("#addUrl").click(function () {
    var link = $("#new_link").val();
    if (link.length > 0) {
        $(".links").empty();
        $(".links").append("<div><a href='" + link + "'>" + link + "</a>");
        $(".links").append("<input type='hidden' name='link' value='" + link + "'/><br/></div>");

        getLinkMeta(link);
        $("#add_link").attr("disabled", "disabled");
    }
});