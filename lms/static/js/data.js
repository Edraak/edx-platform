function get_dummy_map(value_type) {

	return {
		"type": "map",
		"value_type": value_type,
		"courses": [
			{
				"run": "2013_Spring",
				"course_name": "6.00x",
				"org": "MITx",
				"value": 50
			},
			{
				"run": "2013_Spring",
				"course_name": "7.00x",
				"org": "MITx",
				"value": 40
			},
			{
				"run": "2013_Spring",
				"course_name": "8.02x",
				"org": "MITx",
				"value": 20
			}
		]
	};
}

function get_dummy_timeseries(value_type){
	var today = (new Date()).getTime();
	var yesterday = today - 86400000;
	var day_before_yesterday = today - 86400000*2;

	return {
		"type": "timeseries",
		"value_type": value_type,
		"all_series": [
			{
				"label": "edX",
				"data": [
					[today, 100], [yesterday, 200], [day_before_yesterday, 350]
					]
			},
			{
				"label": "6.00x",
				"data": [
					[today, 50], [yesterday, 60], [day_before_yesterday, 45]
					]
			}
		]
	};
}

function render_timeline(data, target){
	/*
	This function takes an object containing the following:
	    value_type, which is a display name for the series
        all_series, an array of objects containing the timeseries data
           and some information about that series ()
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

	// edX series in gray, all other series edX purple but hidden until revealed
	data["all_series"].forEach(function(x) {
		if (x["label"] === "edX") {
			x["color"] = "rgb(119, 121, 124)";
		} else {
			x["color"] = "rgb(165, 16, 86)";
		}	
	
		return x;
	})
	$.plot(target, data["all_series"], {
		xaxis: {
                mode: "time",
                minTickSize: [1, "day"],
                timeformat: "%m/%e"
            	}})
}

function render_map(data, target) {
	var course_bars = [];
	var course_names = [];
	var i = 0;

	data["courses"].forEach(function (x) {
		course_bars.push([i-.25, x["value"]]);
		course_names.push([i, x["course_name"]]);
		i++;
	})

	$.plot(target, [
		{
			label: data["value_type"],
			data: course_bars,
		 	bars: {
		 		show: true,
		 		barWidth: .5
		 	},
		 	color: "rgb(13, 139, 227)"
		}
		], {
			xaxis: {
				ticks: course_names
			}
		});
}

function fake_ajax(url, callback) {
	urls = {
		'/data/enrollments/last': get_dummy_map("enrollments"),
		'/data/enrollments/timeseries': get_dummy_timeseries("enrollments"),
		
		'/data/enrollment_conversion/last': get_dummy_map("enrollment_conversion"),
		'/data/enrollment_conversion/timeseries': get_dummy_timeseries("enrollment_conversion"),
		
		'/data/participation_conversion/last': get_dummy_map("participation_conversion"),
		'/data/participation_conversion/timeseries': get_dummy_timeseries("participation_conversion"),

		'/data/certification_conversion/last': get_dummy_map("certification_conversion"),
		'/data/certification_conversion/timeseries': get_dummy_timeseries("certification_conversion"),

	}
	data = urls[url];
	callback(data);
}

function load_and_plot(url, target) {
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
	fake_ajax(url, callback);
}

function add_graph_section(base_url) {
	section = $("<section>").addClass("graph_section");
	map_div = $("<div>").addClass('map').text("map");
	series_div = $("<div>").addClass('timeseries').text("series");
	title = $("<h2>"+base_url+"</h2>");

	section.append(title);
	section.append(map_div);
	section.append(series_div);
	$('#graphs_container').append(section);
	$('#graphs_container').append("<br style='clear:both'/>");
	
	load_and_plot(base_url + '/last', map_div);
	load_and_plot(base_url + '/timeseries', series_div);
}

$(document).ready(function() {

	add_graph_section('/data/enrollments');
	add_graph_section('/data/enrollment_conversion');	
	add_graph_section('/data/participation_conversion');	
	add_graph_section('/data/certification_conversion');	
	
});

