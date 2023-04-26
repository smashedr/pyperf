$(document).ready(function() {

    const pk = JSON.parse(document.getElementById('pk').textContent);

    $.ajax({
        url: '/ajax/' + pk + '/graph/',
        type: 'GET',
        beforeSend: function( jqXHR ){
            $('.graph-loading').toggle();
        },
        success: function(data, textStatus, jqXHR){
            console.log('Status: '+jqXHR.status+', Data: '+data);
            $('#graph-data').prepend(data);
        },
        complete: function(){
            console.log('graph loaded');
            $('.graph-loading').toggle();
        },
        error: function(data, textStatus) {
            console.log('Status: '+data.status+', Response: '+data.responseText);
        },
    });

    $.ajax({
        url: '/ajax/' + pk + '/map/',
        type: 'GET',
        beforeSend: function( jqXHR ){
            $('.map-loading').toggle();
        },
        success: function(data, textStatus, jqXHR){
            console.log('Status: '+jqXHR.status+', Data: '+data);
            $('#map-data').prepend(data);
        },
        complete: function(){
            console.log('map loaded');
            $('.map-loading').toggle();
        },
        error: function(data, textStatus) {
            console.log('Status: '+data.status+', Response: '+data.responseText);
        },
    });

});
