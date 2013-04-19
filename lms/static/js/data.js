
function get_enrollment_data(callback) {
	var today = (new Date()).getTime();
	var yesterday = (new Date()).getTime();
	var today = (new Date()).getTime();

	var dummy_data = {
		"value_type": "Enrollments (Last 7 Days)",
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
	callback(dummy_data); 
}

function render_chart(data) {
	$('#json_goes_here').text(String(data));
	var chart_div = $("<div class='course_by_course'>flot should replace this</div>");

	var course_bars = [];
	var course_names = [];
	var i = 0;
	data["courses"].forEach(function (x) {
		course_bars.push([i-.25, x["value"]]);
		course_names.push([i, x["course_name"]]);
		i++;
	})
	// $.plot(chart_div, [{
	// 			label: "Norway",
	// 			data: [[1988, 4382], [1989, 4498], [1990, 4535], [1991, 4398], [1992, 4766], [1993, 4441], [1994, 4670], [1995, 4217], [1996, 4275], [1997, 4203], [1998, 4482], [1999, 4506], [2000, 4358], [2001, 4385], [2002, 5269], [2003, 5066], [2004, 5194], [2005, 4887], [2006, 4891]]
	// 		},{
	// 			label: "Sweden",
	// 			data: [[1988, 6402], [1989, 6474], [1990, 6605], [1991, 6209], [1992, 6035], [1993, 6020], [1994, 6000], [1995, 6018], [1996, 3958], [1997, 5780], [1998, 5954], [1999, 6178], [2000, 6411], [2001, 5993], [2002, 5833], [2003, 5791], [2004, 5450], [2005, 5521], [2006, 5271]]
	// 		}], {
	// 				yaxis: {
	// 					min: 0
	// 				},
	// 				xaxis: {
	// 					tickDecimals: 0
	// 				}
	// 			});
	$('#graphs_container').append(chart_div);
	$.plot(chart_div, [
		{
			label: data["value_type"],
			data: course_bars,
		 	bars: {
		 		show: true,
		 		barWidth: .5
		 	}
		}
		], {
			xaxis: {
				ticks: course_names
			}
		});
}

$(document).ready(function() {
	get_enrollment_data(render_chart)
});

