$(document).ready(function() {

    // Log out form click function
    $(".log-out").on("click", function () {
        $("#log-out").submit();
        return false;
    });

    // Init a ClipboardJS attribute
    new ClipboardJS('.clip');

});
