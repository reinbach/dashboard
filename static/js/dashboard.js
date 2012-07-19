$(function() {
    // Open up a connection to our server
    var socket = io.connect();

    // Just update our conn_status field with the connection status
    socket.on('connect', function() {
        $('#conn_status').html('<b>Connected</b>');
	$('#conn_status').attr("class", "label label-success")
	// this is the call that streams the events being added
	socket.emit('stream', '');
    });
    socket.on('error', function() {
        $('#conn_status').html('<b>Error</b>');
	$('#conn_status').attr("class", "label label-important")
    });
    socket.on('disconnect', function() {
        $('#conn_status').html('<b>Closed</b>');
	$('#conn_status').attr("class", "label label-warning")
    });

    // getting a list of meta data types
    socket.on('meta_data_types', function(data) {
	var d = $.parseJSON(data);
	$("#meta_data_types").append("<li>" + d.label + "</li>");
    });
});
