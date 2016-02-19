var script = document.createElement('script');
script.src = 'http://code.jquery.com/jquery-1.11.0.min.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);


$(function() {
    $('#btnDelete').click(function() {
        $.ajax({
            url: '/albums/edit',
            data: {'op': "delete"},
            type: 'POST',
            success: function(response) {
                console.log(response);
                location.reload();
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});