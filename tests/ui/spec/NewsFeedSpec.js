describe("NewsFeed", function() {

  it("should be able to click a like button", function() {
    loadFixtures("NewsFeedFixture.html");
    Newsfeed.handleLikeButton();
    $("#like-btn").click();
    expect($("#like-btn").attr('class')).toBe("unlike");
  });
});
