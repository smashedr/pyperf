$(document).ready(function() {

    const pk = JSON.parse(document.getElementById('pk').textContent);

    $.ajax({
        url: '/ajax/graph/',
        type: 'POST',
        data: {pk: pk},
        dataType: 'text',
        beforeSend: function( jqXHR ){
            console.log('beforeSend');
            $('.graph-loading').toggle();
        },
        success: function(data, textStatus, jqXHR){
            console.log('Status: '+jqXHR.status+', Data: '+data);
            $('#graph-data').prepend(data);
        },
        complete: function(){
            console.log('complete');
            $('.graph-loading').toggle();
        },
        error: function(data, textStatus) {
            console.log('Status: '+data.status+', Response: '+data.responseText);
        },
    });

    $.ajax({
        url: '/ajax/map/',
        type: 'POST',
        data: {pk: pk},
        dataType: 'text',
        beforeSend: function( jqXHR ){
            console.log('beforeSend');
            $('.map-loading').toggle();
        },
        success: function(data, textStatus, jqXHR){
            console.log('Status: '+jqXHR.status+', Data: '+data);
            $('#map-data').prepend(data);
        },
        complete: function(){
            console.log('complete');
            $('.map-loading').toggle();
        },
        error: function(data, textStatus) {
            console.log('Status: '+data.status+', Response: '+data.responseText);
        },
    });

});
