$(document).ready(function () {
  // Initialize components
  $(".sidenav").sidenav({ edge: "right" });
  $("select").formSelect();
  $(".carousel.carousel-slider").carousel({
    fullWidth: true,
    indicators: true,
  });
    $('.modal').modal();
});
