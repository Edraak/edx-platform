<%page args="id_str_opened, id_str_grade, id_str_attempts, id_str_tooltip, data_opened, data_grade, data_attempts, i, **kwargs"/>
<%!
  import json
%>

$(function () {
  var divTooltip = d3.select("#${id_str_tooltip}");
  
  var paramOpened = {
    data: ${json.dumps(data_opened)},
    width: $("#${id_str_opened}").width(),
    height: $("#${id_str_opened}").height()-25, // Account for header
    tag: "opened",
    bVerticalXAxisLabel : true,
    bLegend : false,
    margin: {left:0},
  };

  var paramGrade = {
    data: ${json.dumps(data_grade)},
    width: $("#${id_str_grade}").width(),
    height: $("#${id_str_grade}").height()-25, // Account for header
    tag: "grade",
  };

  var paramAttempts = {
    data: ${json.dumps(data_attempts)},
    width: $("#${id_str_attempts}").width(),
    height: $("#${id_str_attempts}").height()-25, // Account for header
    tag: "attempts",
  };

  var barGraphOpened, barGraphGrade, barGraphAttempts;

  if ( paramOpened.data.length > 0 ) {
    barGraphOpened = edx_d3CreateStackedBarGraph(paramOpened, d3.select("#${id_str_opened}").append("svg"), divTooltip);
    barGraphOpened.scale.stackColor.range(["#555555","#555555"]);
    barGraphOpened.drawGraph();
  }

  if ( paramGrade.data.length > 0 ) {
    barGraphGrade = edx_d3CreateStackedBarGraph(paramGrade, d3.select("#${id_str_grade}").append("svg"), divTooltip);

    barGraphGrade.scale.stackColor.domain([0,50,100]).range(["#e13f29","#cccccc","#17a74d"]);
    barGraphGrade.legend.width += 2;

    barGraphGrade.drawGraph();
  }

  if ( paramAttempts.data.length > 0 ) {
    barGraphAttempts = edx_d3CreateStackedBarGraph(paramAttempts, d3.select("#${id_str_attempts}").append("svg"),
                                                   divTooltip);
    barGraphAttempts.scale.stackColor
      .range(["#c3c4cd","#b0b4d1","#9ca3d6","#8993da","#7682de","#6372e3",
              "#4f61e7","#3c50eb","#2940ef","#1530f4","#021ff8"]);
    barGraphAttempts.legend.width += 2;

    barGraphAttempts.drawGraph();
  }
});