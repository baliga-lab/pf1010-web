$("#like-btn").click(function () {
    var btn = $(this);
    if (btn.hasClass("like")) {
        btn.removeClass('like').addClass('unlike');
    } else {
        btn.removeClass('unlike').addClass('like');
    }
});