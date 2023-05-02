$(document).ready(function() {

    // Log out form click function
    $('.log-out').on('click', function () {
        $('#log-out').submit();
        return false;
    });

    // Show custom toast-alert classes on load
    $(".toast-alert").each(function() {
        console.log($(this).html());
        let toastAlert = new bootstrap.Toast($(this));
        toastAlert.show();
    });

    // Init a ClipboardJS attribute
    new ClipboardJS('.clip');

});
