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


    var margin = [40, 40, 40, 40]
    var width = 650 - margin[1] - margin[3];
    var height = 200 - margin[0] - margin[2];

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

            var chart_height = height;

            // setup charts/graphs
	    var chart_group_id = getChartGroupId(meta.collection_id);
            var chart_div = "<div id='" + chart_group_id + "' class='chart-group'><h3>" + meta.label + "</h3></div>";
            $("#chart-container").append(chart_div);

            for (i = 0; i < meta.data.length; i++) {
                var data = meta.data[i];
      	        createChart(data, chart_group_id, chart_height);
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

    function createChart(data, chart_group_id, chart_height) {
        // create the relevant charts
      	var max = d3.max(data)

      	// scales
      	var x = d3.scale.linear().domain([0, data.length - 1]).range([0, width]);
      	var y = d3.scale.linear().domain([0, max]).range([chart_height, 0]);

      	var chart = d3.select("#" + chart_group_id)
            .append("svg:svg")
      	    .attr("class", "chart")
      	    .attr("width", width + margin[1] + margin[3])
      	    .attr("height", chart_height + margin[0] + margin[2])
            .append("svg:g")
            .attr("transform", "translate(" + margin[3] + ", " + margin[0] + ")");

        setYAxis(chart, y);

      	chart.selectAll("path.line")
      	    .data([data])
      	    .enter().append("svg:path")
      	    .attr("d", d3.svg.line()
      	     	  .x(function(d, i) { return x(i); })
      	     	  .y(y)
      	     	 );
    }

    function setYAxis(chart, y) {
        var yAxis = d3.svg.axis()
            .scale(y)
            .ticks(4)
            .orient("left");

        if (!$("svg:g", chart).length) {
            chart.append("svg:g");
            chart_axis = $("svg:g", chart);
        }

        chart.append("svg:g").attr("class", "y axis")
            .attr("transform", "translate(0, 0)")
            .call(yAxis);
    }

    function updateChart(collection_id, data) {
        // update the chart by adding new data
        // and removing old data

        var chart_height = height;

        //TODO handle the scenario when this is the new chart
        var chart_group_id = getChartGroupId(collection_id);
        var paths = $("#" + chart_group_id + " path[class!='domain']");

        for (i = 0; i < data.length; i++) {
            var chart_path = d3.select(paths[i]);
            var chart_data = chart_path.data()[0];

            // need to push the data onto the relevant data array
            chart_data.push(data[i][0]);

            // pop the old data point off the front
            // only if the count has reached the max
            // max value hardcoded at the moment
            if (chart_data.length > 100) {
                chart_data.shift();
            }

            // scales
      	    var max = d3.max(chart_data);
      	    var x = d3.scale.linear().domain([0, chart_data.length - 1]).range([0, width]);
            var y = d3.scale.linear().domain([0, max]).range([chart_height, 0]);

            // redraw line and slide to the left
            chart_path
                .attr("d", d3.svg.line()
      	     	      .x(function(d, i) { return x(i); })
      	     	      .y(y)
                     )
                .attr("transform", null)
                .transition()
                .ease("linear");

            setYAxis(d3.select("#" + chart_group_id), y);
        }
    }
});
