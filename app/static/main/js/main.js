$(document).ready(function() {

    // Back to Top Button, Function, and Listener
    let mybutton = document.getElementById("btn-back-to-top");
    window.onscroll = function () {
      scrollFunction();
    };
    function scrollFunction() {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            mybutton.style.display = "block";
        } else {
            mybutton.style.display = "none";
        }
    }
    mybutton.addEventListener("click", backToTop);
    function backToTop() {
      document.body.scrollTop = 0;
      document.documentElement.scrollTop = 0;
    }

    // Show custom toast-alert classes on load
    $(".toast-alert").each(function() {
        console.log($(this).html());
        let toastAlert = new bootstrap.Toast($(this));
        toastAlert.show();
    });

    // Init a ClipboardJS attribute
    new ClipboardJS('.clip');

});
