$(document).ready(function () {
    $("#side-toggle").click(function () {
		$("#side-float").toggleClass("visible").fadeToggle(200);
		$('#side-float').fadeToggle(2000);
    });
});