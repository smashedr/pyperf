$(document).ready(function() {

    // Reload page on browser back/forward
    //  $(window).on('popstate', function() {
    //      location.reload(true);
    //  });
    var perfEntries = performance.getEntriesByType("navigation");
    if (perfEntries[0].type === "back_forward") {
        location.reload();
    }

    // Monitor websockets for new data
    const socket = new WebSocket("wss://" + window.location.host + "/ws/home_group/");
    console.log('Websockets Connected.');
    socket.onmessage = function(event) {
        let data = JSON.parse(event.data);
        $.post("/ajax/tdata/", {"pk": data.pk}, function(response) {
            $("#results tbody").prepend(response);
            console.log('Table Updated.');
        });
    };

});
