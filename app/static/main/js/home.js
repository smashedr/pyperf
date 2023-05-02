$(document).ready(function() {

    // Reload page on browser back/forward
    let perfEntries = performance.getEntriesByType('navigation');
    if (perfEntries[0].type === 'back_forward') {
        let reloadSession = localStorage.getItem('reloadSession');
        if (reloadSession === 'true') {
            localStorage.removeItem('reloadSession');
            location.reload();
        }
    }

    // Monitor websockets for new data
    const socket = new WebSocket('wss://' + window.location.host + '/ws/home_group/');
    console.log('Websockets Connected.');
    socket.onmessage = function(event) {
        let data = JSON.parse(event.data);
        $.get('/ajax/tdata/' + data.pk, function(response) {
            $('#results tbody').prepend(response);
            localStorage.setItem('reloadSession', 'true');
            console.log('Table Updated.');
        });
    };

});
