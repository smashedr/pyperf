$(document).ready(function() {

    // Get and set the csrf_token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Define Hook Modal and Delete handlers
    const deleteHookModal = new bootstrap.Modal('#delete-hook-modal', {});
    let hookID;
    $('.delete-webhook-btn').click(function () {
        hookID = $(this).data('hook-id');
        console.log(hookID);
        deleteHookModal.show();
    });
    $('#confirm-delete-hook-btn').click(function () {
        if ($('#confirm-delete-hook-btn').hasClass('disabled')) { return; }
        console.log(hookID);
        $.ajax({
            type: 'POST',
            url: `/ajax/delete/hook/${hookID}/`,
            headers: {'X-CSRFToken': csrftoken},
            beforeSend: function () {
                console.log('beforeSend');
                $('#confirm-delete-hook-btn').addClass('disabled');
            },
            success: function (response) {
                console.log('response: ' + response);
                deleteHookModal.hide();
                console.log('removing #wehook-' + hookID);
                let count = $('#webhooks-table tr').length;
                $('#webhook-' +hookID).remove();
                if (count<=2) {
                    console.log('removing #webhooks-table@ #webhooks');
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
                $('#confirm-delete-hook-btn').removeClass('disabled');
            }
        });
    });

    // // Define Hook Modal and Delete handlers
    // const deleteResultModal = new bootstrap.Modal('#delete-result-modal', {});
    // let resultID;
    // $('.delete-result-btn').click(function () {
    //     resultID = $(this).data('result-id');
    //     console.log(resultID);
    //     deleteResultModal.show();
    // });
    // $('#confirm-delete-result-btn').click(function () {
    //     if ($('#confirm-delete-result-btn').hasClass('disabled')) { return; }
    //     console.log(resultID);
    //     $.ajax({
    //         type: 'POST',
    //         url: `/ajax/delete/result/${resultID}/`,
    //         headers: {'X-CSRFToken': csrftoken},
    //         beforeSend: function () {
    //             console.log('beforeSend');
    //             $('#confirm-delete-result-btn').addClass('disabled');
    //         },
    //         success: function (response) {
    //             console.log('response: ' + response);
    //             deleteResultModal.hide();
    //             console.log('removing #result-' + resultID);
    //             let count = $('#results-table tr').length;
    //             $('#result-' +resultID).remove();
    //             let message = 'Result ' + resultID + ' Successfully Removed.';
    //             show_toast(message,'success');
    //         },
    //         error: function (xhr, status, error) {
    //             console.log('xhr status: ' + xhr.status);
    //             console.log('status: ' + status);
    //             console.log('error: ' + error);
    //             deleteResultModal.hide();
    //             let message = xhr.status + ': ' + error
    //             show_toast(message,'danger', '15000');
    //         },
    //         complete: function () {
    //             console.log('complete');
    //             $('#confirm-delete-result-btn').removeClass('disabled');
    //         }
    //     });
    // });

});
