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
        var meta_id = "meta-" + d.collection_id;
        if ($("#" + meta_id).length == 0) {
            $("#meta_data_types").append(
                "<li><span class='label label-info' id='" +
                    meta_id + "'>" + d.label + "</span></li>"
            );

            // setup charts/graphs
	    var chart_id = "chart-" + d.collection_id;
            var chart_div = "<div id='" + chart_id + "' class='chart-group'><h3>" + d.label + "</h3></div>";
            $("#chart-container").append(chart_div);

      	    var width = 700;
      	    var height = 300 / d.data.length;
            for (i = 0; i < d.data.length; i++) {
                var data = d.data[i];
      	        createChart(data, chart_id, width, height);
            }

            // toggle the display of graph for particular feed
            $("#" + meta_id).click(function() {
                $("#" + chart_id).toggle();
            });
	}
    });
    function createChart(data, chart_id, width, height) {
      	var max = d3.max(data)

      	// scales
      	var x = d3.scale.linear().domain([0, data.length - 1]).range([0, width]);
      	var y = d3.scale.linear().domain([0, max]).range([height, 0]);

      	var chart = d3.select("#" + chart_id).append("svg:svg")
      	    .attr("class", "chart")
      	    .attr("width", width)
      	    .attr("height", height);

      	chart.selectAll("path.line")
      	    .data([data])
      	    .enter().append("svg:path")
      	    .attr("d", d3.svg.line()
      	     	  .x(function(d, i) { return x(i); })
      	     	  .y(y)
      	     	 );
    }
});
