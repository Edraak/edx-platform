<%page args="sandbox_stuff, **kwargs"/>
<%!
  import json
%>

$(function () {
  var d3_prob_grade_distrib = ${json.dumps(sandbox_stuff['d3_prob_grade_distrib'])}
  console.log(d3_prob_grade_distrib);

  var svg = d3.select("#viz").append("svg");
  var div = d3.select("#viz").append("div");
  var param = {
    data: d3_prob_grade_distrib,
    width: 1000,
    height: 1000,
    bVerticalXAxisLabel: true,
  };
  var barGraph = edx_d3CreateStackedBarGraph(param, svg, div);
  barGraph.drawGraph();
});