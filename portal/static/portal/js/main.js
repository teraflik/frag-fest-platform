$(document).ready(function () {
    $("#side-toggle").click(function () {
      $("#side-float").toggleClass("visible");
      $("#side-toggle i").toggleClass("fa-chevron-circle-left fa-chevron-circle-right");
      return false;
    });
    $('body').on('mouseenter mouseleave','.dropdown',function(e){
      var _d=$(e.target).closest('.dropdown');_d.addClass('show');
      setTimeout(function(){
        _d[_d.is(':hover')?'addClass':'removeClass']('show');
      },300);
    });
});