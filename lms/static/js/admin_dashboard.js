function render_timeline(data, target){
	/*
	This function takes an object containing the following:
	    value_type, which is a display name for the series
        all_series, an array of objects containing the timeseries data
           and a label for that series ()
	example:
	{
		"type": "timeseries",
		"value_type": "Enrollments per Day",
		"all_series": [
			{
				"label": "edX Total",
				"data": [
					[1239410294831, 100], [1234210419238, 200], [1234210419238, 350]
					]
			},
			{
				"label": "6.00x",
				"data": [
					[1239410294831, 50], [1234210419238, 60], [1234210419238, 45]
					]
			}
		]
	}

	*/

	// first series in gray, all other series get default colors
	series_no = 1;
	data["all_series"].forEach(function(x) {
		if (series_no==1) {
			x["color"] = "rgb(119, 121, 124)";
			x["lines"] = { 
				show: true,
				fill: true
			};
		} else if (series_no==2) {
			x["color"] = "rgb(13, 139, 227)";
			x["lines"] = { 
				show: true,
				fill: true
			};
		}	
		series_no += 1;
	
		return x;
	})
	$.plot(target, data["all_series"], {
		xaxis: {
                mode: "time",
                minTickSize: [1, "day"],
                min: Math.max(1343019600000, data["all_series"][0]["data"][0][0]),
                timeformat: "%m/%e"
            	}})
}

function render_map(data, target) {
	// resize the div (height) based on 
	// number of entries
	entries = data["courses"].length
	target.height(20*entries);

	var course_bars = [];
	var course_names = [];
	var i = 0;

	data["courses"].sort(function(a, b) {
		return a.value-b.value
	})

	data["courses"].forEach(function (x) {
		if (x["value"] > 10) {
			course_bars.push([ x["value"], i-.4]);
			course_names.push([i, x["course_name"] + " (" + x["org"] + ", " + x["run"] + ")"]);
			i++;
		}
	})

	$.plot(target, [
		{
			label: data["value_type"],
			data: course_bars,
		 	bars: {
		 		show: true,
		 		barWidth: .8,
		 		horizontal: true,
		 	},
		 	color: "rgb(13, 139, 227)"
		}
		], {
			yaxis: {
				ticks: course_names
			},
			xaxis: {
				position: "top"
			}

		});
}

function load_and_plot(url, target, fake) {
	function callback(data) {
		// TODO: if error, complain
		if (data["type"] === "timeseries") {
			render_timeline(data, target);
		} else if (data["type"] === "map") {
			render_map(data, target)
		}
	};

	// TODO: do ajax calls here
	// $.post(url, callback)
	if (fake) {
		fake_ajax(url, callback);
	} else {
		$.get(url, callback);
	}
}

function add_flot_chart(div_id, chart_class, data_url, render_fn) {
	section = $("<section>").addClass(div_id);
	chart_div = $("<div>").addClass(chart_class).text("loading...");

	section.append(chart_div);
	$('#'+div_id).append(section);

	render_fn(data_url, chart_div, false);
}

$(document).ready(function() {

	add_flot_chart('daily_enrollments', 'timeseries', '/data/enrollment_history/timeseries', load_and_plot);
	add_flot_chart('weekly_course_enrollments', 'map', '/data/enrollment_history/map', load_and_plot);
	
});

