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

  // Test code to make sure D3 working
  // Adds an svg element to the div and sets it's size
  var sampleSVG = d3.select("#viz")
    .append("svg")
    .attr("width", 500)
    .attr("height", 500);    
  
  sampleSVG.append("circle")
    .style("stroke", "gray")
    .style("fill", "white")
    .attr("r", 50)
    .attr("cx", 100)
    .attr("cy", 200)
    .on("click", animate4)
    .on("dblclick", animate1);
  
  function animate1() {
    var element = d3.select(this);
        element.transition()
      .duration(1000)
      .attr("cx",element.attr("cx") - 10);
  }
  
  function animate4() {
    var r = 10 + Math.floor(Math.random()*80);
    var x = r + Math.floor(Math.random()*(500-r*2));
    var y = r + Math.floor(Math.random()*(500-r*2));
    var rColor = Math.floor(Math.random()*255);
    var gColor = Math.floor(Math.random()*255);
    var bColor = Math.floor(Math.random()*255);
    d3.select(this)
      .transition()
      .duration(1000)
      .attr("r", r)
      .transition()
      .delay(1000)
      .duration(1000)
      .attr("cy", y)
      .attr("cx", x)
            .style("fill", "rgb("+rColor+","+gColor+","+bColor+")");
    
  }
  
});