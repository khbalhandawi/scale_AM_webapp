function plot_contour() {
  var json = {};

  // kernel bandwidth
  var sliderElement = document.getElementById("slide");
  if (sliderElement.value <= 50)
    json["bandwidth"] = 10**(0.02*(sliderElement.value-50)); // log scale
  else
    json["bandwidth"] = 9/5 * (sliderElement.value - 50) + 1; // linear scale

  // plot axes and nominal values
  json["x-axis"] = getRadioValue("axis-"+1);
  json["y-axis"] = getRadioValue("axis-"+2);
  json["z-axis"] = getRadioValue("z-axis");
  
  var nominalElements = document.getElementsByName("nominal");
  for (const element of nominalElements) {
    json["nominal"] = (json["nominal"] || []).concat([element.value]);
  }

  // change effect and monotonicity
  var changeElements = document.getElementsByName("change");
  for (const element of changeElements) {
    json["change_effect"] = (json["change_effect"] || []).concat([element.value]);
  }

  var monotonicityElements = document.getElementsByName("monotonicity");
  for (const element of monotonicityElements) {
    json["monotonicity"] = (json["monotonicity"] || []).concat([element.value]);
  }

  // Jacobian
  json["Jacobian"] = getJacobian();

  // Resolution
  var numberElement = document.getElementById("resolution");
  json["resolution"] = numberElement.value;

  // Intersection
  var checkboxElement = document.getElementById("intersect");
  json["intersect"] = checkboxElement.checked;

  var jsonStr=JSON.stringify(json);
  console.log(jsonStr);

  $.ajax({
    url: "/api/predict",
    type: "POST",
    contentType: "application/json",
    dataType : "json",
    data : jsonStr,
    success: function(response) {
      console.log(response.x);
      console.log(response.y);
      console.log(response.z);

      canvas = document.getElementById("canvas");

      var data = [{
          z: response.z,
          x: response.x,
          y: response.y,
          type: "contour",
          opacity: 0.6,
          colorbar:{
            title: response.labels["zlabel"],
            side: "top",
            titlefont: {
              size: 14,
              family: "Arial, sans-serif"
            },
            borderwidth: 1,
            xpad: 10
          },
          showlegend: false
      }];

      var layout = {
        xaxis: {
          title: response.labels["xlabel"]
        },
        yaxis: {
          title: response.labels["ylabel"]
        },
        legend: {
          yanchor:'top',
          xanchor:'center',
          "orientation": "h",
          x: 0.5,
          y: 1.1,
          font: {
            size: 14
          },
          borderwidth: 1
        }
      };  
      
      Plotly.newPlot(canvas, data, layout);
      
      var colors = ["#8f0eff", "#2ca02c", "#0000ff", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
      var i = 0
      for (const cstr of response.cstrs) {
          var color = colors[cstr.order % colors.length]
          var color_1 = colors[(cstr.order+1) % colors.length]
          var cs = [
              ["0.0", color],
              ["1.0", color_1]
          ];

          var j = {
              z: cstr.values_line,
              x: response.x,
              y: response.y,
              opacity: 0.5,
              ncontours : 2,
              type: "contour",
              colorscale: cs,
              showscale: false,
              line:{
                  smoothing: 1.0,
                  width: 5.0
              },
              contours:{
                  coloring: "lines"
              },
              hoverinfo: "skip",
              showlegend: false
          };
          // data.push(j);
          // add a single trace to an existing graphDiv
          Plotly.addTraces(canvas, j);

          var cs = [
            ["0.0", color],
            ["1.0", color]
          ];
          var j = {
              z: cstr.values,
              x: response.x,
              y: response.y,
              name: cstr.label,
              opacity: 0.3,
              ncontours : 2,
              type: "contour",
              colorscale: cs,
              showscale: false,
              hoverinfo: "skip",
              showlegend: true
          };
          // data.push(j);
          // add a single trace to an existing graphDiv
          Plotly.addTraces(canvas, j);
          i++;
      }
      return;
    },
    error: function(err) {
      console.log(err);
    }
  });
  return false;
}