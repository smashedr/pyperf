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

    // Set the csrf_token and init flush-cache button
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    $("#flush-cache").click(function () {
        console.log('flush-cache clicked...');
        $.ajax({
            type: 'POST',
            url: '/flush-cache/',
            headers: {'X-CSRFToken': csrftoken}
        }).done(function(data) {
            alert('Cache flush request sent...');
        });
        return false;
    });

});
