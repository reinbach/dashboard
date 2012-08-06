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
        setUpChart(d);
    });

    // getting new data
    socket.on('new_data', function(data) {
        var d = $.parseJSON(data);
        setUpChart(d);
        updateChart(d.collection_id, d.data);
    });

    function setUpChart(meta) {
        // if chart setup does not exist for the meta
        // go ahead and create the setup
        // and create the relevant charts with the data
        // provided
        var meta_id = "meta-" + meta.collection_id;
        if ($("#" + meta_id).length == 0) {
            $("#meta_data_types").append(
                "<li><span class='label label-info' id='" +
                    meta_id + "'>" + meta.label + "</span></li>"
            );

            // setup charts/graphs
	    var chart_group_id = getChartGroupId(meta.collection_id);
            var chart_div = "<div id='" + chart_group_id + "' class='chart-group'><h3>" + meta.label + "</h3></div>";
            $("#chart-container").append(chart_div);

      	    var width = 700;
      	    var height = 300 / meta.data.length;
            for (i = 0; i < meta.data.length; i++) {
                var data = meta.data[i];
      	        createChart(data, chart_group_id, width, height);
            }

            // toggle the display of graph for particular feed
            $("#" + meta_id).click(function() {
                $("#" + chart_group_id).toggle();
            });
	}
    }

    function getChartGroupId(collection_id) {
        return "chart-" + collection_id;
    }

    function createChart(data, chart_group_id, width, height) {
        // create the relevant charts
      	var max = d3.max(data)

      	// scales
      	var x = d3.scale.linear().domain([0, data.length - 1]).range([0, width]);
      	var y = d3.scale.linear().domain([0, max]).range([height, 0]);

      	var chart = d3.select("#" + chart_group_id).append("svg:svg")
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

    function updateChart(collection_id, data) {
        // update the chart by adding new data
        // and removing old data

        var width = 700
        var height = 300 / data.length;

        //TODO handle the scenario when this is the new chart
        var chart_group_id = getChartGroupId(collection_id);
        var charts = $("#" + chart_group_id + " svg");
        var paths = d3.selectAll("#" + chart_group_id + " path");
        for (i = 0; i < data.length; i++) {
            var chart = d3.select(charts[i]).select("path");
            var chart_data = chart.data()[0]
            // need to push the data onto the relevant data array
            chart_data.push(data[i][0])

            // scales
      	    var max = d3.max(chart_data);
      	    var x = d3.scale.linear().domain([0, chart_data.length - 1]).range([0, width]);
            var y = d3.scale.linear().domain([0, max]).range([height, 0]);

            // redraw line and slide to the left
            chart
                .attr("d", d3.svg.line()
      	     	      .x(function(d, i) { return x(i); })
      	     	      .y(y)
                     )
                .attr("transform", null)
                .transition()
                .ease("linear")
                .attr("transform", "translate(" + x(-1) + ")");
            // pop the old data point off the front
            chart_data.shift()
        }
    }
});
