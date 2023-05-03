$(document).ready(function() {

    // Get and set the csrf_token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Init the logout form click function
    $('.log-out').on('click', function () {
        $('#log-out').submit();
        return false;
    });

    // Init the flush-cache click function
    $('#flush-cache').click(function () {
        console.log('flush-cache clicked...');
        $.ajax({
            type: 'POST',
            url: '/flush-cache/',
            headers: {'X-CSRFToken': csrftoken},
            beforeSend: function () {
                console.log('beforeSend');
            },
            success: function (response) {
                console.log('response: ' + response);
                alert('Cache Flush Successfully Sent...');
            },
            error: function (xhr, status, error) {
                console.log('xhr status: ' + xhr.status);
                console.log('status: ' + status);
                console.log('error: ' + error);
                alert('Error: ' + xhr.responseText)
            },
            complete: function () {
                console.log('complete');
                location.reload();
            }
        });
        return false;
    });

    // Define Hook Modal and Delete handlers
    const deleteHookModal = new bootstrap.Modal('#delete-hook-modal', {});
    let hookID;

    $('.delete-webhook-btn').click(function () {
        hookID = $(this).data('hook-id');
        console.log(hookID);
        deleteHookModal.show();
    });

    $('#confirm-delete-btn').click(function () {
        if ($('#confirm-delete-btn').hasClass('disabled')) { return; }
        console.log(hookID);
        $.ajax({
            type: 'POST',
            url: `/ajax/delete/hook/${hookID}/`,
            headers: {'X-CSRFToken': csrftoken},
            beforeSend: function () {
                console.log('beforeSend');
                $('#confirm-delete-btn').addClass('disabled');
            },
            success: function (response) {
                console.log('response: ' + response);
                deleteHookModal.hide();
                $('#webhook-' +hookID).remove();
                let count = $('#webhooks-table tr').length;
                if (count<=2) {
                    $('#webhooks-table').remove();
                    $('#webhooks').remove();
                }
                let message = 'Webhoook ' + hookID + ' Successfully Removed.';
                show_toast(message,'success');
            },
            error: function (xhr, status, error) {
                console.log('xhr status: ' + xhr.status);
                console.log('status: ' + status);
                console.log('error: ' + error);
                deleteHookModal.hide();
                let message = xhr.status + ': ' + error
                show_toast(message,'danger', '15000');
            },
            complete: function () {
                console.log('complete');
                $('#confirm-delete-btn').removeClass('disabled');
            }
        });
    });

});
