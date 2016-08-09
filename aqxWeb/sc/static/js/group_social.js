// Waits Until DOM Is Ready
$(document).ready(function () {

});

/* function : getUserConsent
 # purpose : When the user clicks "Leave" button in the Group page, confirmation pop up appears. Only when
 the user hits ok button, the user shall be removed from the system
 # params : None
 # returns : None
 */
function getUserConsent() {
    if (confirm('Are you sure?')) {
        return true;
    }
    else {
        return false;
    }
}


/* function : list_users_autocomplete
 # purpose : AutoPopulate list of users to add them as Group Member by the logged in user
 # params : None
 # returns : None
 */
function list_users_autocomplete(group_uid, url_to_get_users_to_invite, url_to_add_group_member) {
    $.ajax({
        url: url_to_get_users_to_invite
    }).done(function (data) {
        $("#txtFriendName").autocomplete({
                minLength: 3,
                source: data.user_json_list,
                focus: function (event, ui) {
                    //$("#txtFriendName").val(ui.item.label);
                    return false;
                },
                select: function (event, ui) {
                    $("#txtFriendName").val(ui.item.label);
                    return false;
                }
            })
            .data("ui-autocomplete")._renderItem = function (ul, item) {
            var google_id_of_user_to_add = item.google_id;
            var given_name_of_user_to_add = item.label;
            return $("<li></li>")
                .data("ui-autocomplete-item", item.label)
                .append("<img src='" + item.image_url + "'" + "height='32' width='32'/>" + " " + item.label + " - " + item.organization)
                .appendTo(ul).click(function () {
                    if (confirm("Are you sure you want to invite " + given_name_of_user_to_add + " to this group?")) {
                        $.ajax({
                            type: 'post',
                            url: url_to_add_group_member,
                            data: {
                                google_id: google_id_of_user_to_add,
                                group_uid: group_uid
                            },
                            success: function (result) {
                                alert("You successfully invited " + given_name_of_user_to_add + " !!");
                                location.reload()
                            }
                        });
                    }
                });

        }

    });
}
