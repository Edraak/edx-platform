<%page args="sandbox_stuff, **kwargs"/>
<%!
  import json
%>

$(function () {
  var prob_grade_distrib = ${json.dumps(sandbox_stuff['prob_grade_distrib'])}
  console.log(prob_grade_distrib);

  var data = [];
  for (var key in prob_grade_distrib) {
    var d = {}
    d.xValue = key;
    d.stackData = [];
    for (var key2 in prob_grade_distrib[key]["grade_distrib"]) {
      var ary = prob_grade_distrib[key]["grade_distrib"][key2];
      var bar = {};

      var grade = (ary[0]*100.0)/prob_grade_distrib[key]["max_grade"];

      bar.color = Math.floor(grade);
      bar.value = ary[1];
      bar.tooltip = key+": Grade("+Math.floor(grade)+"%) "+ary[1]+" student(s)";

      d.stackData.push(bar);
    }
    data.push(d);
  }

  console.log("instructor_dashboard.js line 30");
  console.log(data);
  var svg = d3.select("#viz").append("svg");
  var div = d3.select("#viz").append("div");
  var param = {
    data: data,
    width: 1000,
  };
  var barGraph = edx_d3CreateStackedBarGraph(param, svg, div);
  barGraph.drawGraph();
});