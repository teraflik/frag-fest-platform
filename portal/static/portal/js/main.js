$(document).ready(function () {
    $("#side-toggle").click(function () {
      $("#side-float").toggleClass("visible");
      $("#side-toggle i").toggleClass("fa-chevron-circle-left fa-chevron-circle-right");
      return false;
    });
});