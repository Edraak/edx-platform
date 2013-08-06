<%page args="i, data, tag, **kwargs"/>
<%!
  import json
%>

$(function () {
  var data${i} = ${json.dumps(data)}
  console.log("Section ${i}")
  console.log(data${i});

  if (data${i}.length > 0) {
    var svg${i} = d3.select("#class_dashboard_section_${i}").append("svg")
      .attr("id", "attempts_svg_${i}");
    var div${i} = d3.select("#class_dashboard_section_${i}").append("div");
    var param${i} = {
      data: data${i},
      width: 300,
      height: 500,
      tag: "${tag}",
      bVerticalXAxisLabel: true,
    };
    var barGraph${i} = edx_d3CreateStackedBarGraph(param${i}, svg${i}, div${i});
    barGraph${i}.drawGraph();
  } else {
    d3.select("#class_dashboard_section_${i}").append("div")
      .append("p").text("No problems for this section");
  }
});