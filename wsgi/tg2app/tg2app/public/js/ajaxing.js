$(document).ready(function() {
    $.ajax({
        url: '/get_users',
        success: function(json) {
            var users = json.users;
            $("#sandbox").append("<ul>");
            for ( var i = 0; i < users.length; i++ ) {
                $("#sandbox").append("<li>" + users[i]i.email + "</li>");
            }
            $("#sandbox").append("</ul>");
        },
    });
});
