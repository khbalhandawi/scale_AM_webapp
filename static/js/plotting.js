function plot_contour() {
    var json = {};

    var sliderElement = document.getElementById("slide");
    json["bandwidth"] = sliderElement.value;

    json["x-axis"] = getRadioValue("axis-"+1);
    json["y-axis"] = getRadioValue("axis-"+2);
    json["z-axis"] = getRadioValue("z-axis");
    
    var changeElements = document.getElementsByName("change");
    for (const element of changeElements) {
      json["change_effect"] = (json["change_effect"] || []).concat([element.value]);
    }

    var monotonicityElements = document.getElementsByName("monotonicity");
    for (const element of monotonicityElements) {
      json["monotonicity"] = (json["monotonicity"] || []).concat([element.value]);
    }

    json["Jacobian"] = getJacobian();

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

        // var data_1 = [{
        //   z: [[10, 10.625, 12.5, 15.625, 20],
        //       [5.625, 6.25, 8.125, 11.25, 15.625],
        //       [2.5, 3.125, 5., 8.125, 12.5],
        //       [0.625, 1.25, 3.125, 6.25, 10.625],
        //       [0, 0.625, 2.5, 5.625, 10]],
        //   x: [-9, -6, -5 , -3, -1],
        //   y: [0, 1, 4, 5, 7],
        //   type: "contour"
        // }];

        var data = [{
            z: response.z,
            x: response.x,
            y: response.y,
            type: "contour",
            colorbar:{
            title: "Color Bar Title",
            titleside: "right",
            titlefont: {
              size: 14,
              family: "Arial, sans-serif"
            }
            }
        }];

        var layout = {
          title: "Setting the X and Y Coordinates in a Contour Plot"
        };  
        
        Plotly.newPlot(canvas, data, layout);
        
        var colors = ["#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
        var i = 0
        for (const cstr of response.cstrs) {
            color = colors[i % colors.length]
            var cs = [
                ["0.0", color],
                ["1.0", "rgb(49,54,149)"]
            ];

            var j = {
                z: cstr,
                x: response.x,
                y: response.y,
                opacity: 0.5,
                ncontours : 2,
                type: "contour",
                colorscale: cs,
                showscale: false,
                line:{
                    smoothing: 1.0,
                    width: 3.0
                },
                contours:{
                    coloring: "lines"
                }
            };
            // data.push(j);
            // add a single trace to an existing graphDiv
            Plotly.addTraces(canvas, j);

            var j = {
                z: cstr,
                x: response.x,
                y: response.y,
                opacity: 0.2,
                ncontours : 2,
                type: "contour",
                colorscale: cs,
                showscale: false,
            };
            // data.push(j);
            // add a single trace to an existing graphDiv
            Plotly.addTraces(canvas, j);
            i++;
        }
        return
      },
      error: function(err) {
        console.log(err);
      }
    });
    return false
}