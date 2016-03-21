describe("NewsFeed", function() {

  it("should be able to click a like button", function() {
    loadFixtures("likeButton.html");
    Newsfeed.handleLikeButton();
    $("#like-btn").click();
    expect($("#like-btn").attr('class')).toBe("unlike");
  });

    it("should be able to click a unlike button", function() {
    loadFixtures("unlikeButton.html");
    Newsfeed.handleLikeButton();
    $("#like-btn").click();
    expect($("#like-btn").attr('class')).toBe("like");
  });
});
