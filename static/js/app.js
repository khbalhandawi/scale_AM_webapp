function deleteTable(obj) {
    var parent = document.getElementById(obj); 

    if (typeof(parent) != 'undefined' && parent != null && parent.children.length > 0)
    {
        parent.removeChild(parent.children[0]);
    }
}

function addInputTable(n_var,type) {

    console.log(n_var)
    var myTableDiv = document.getElementById(type);
        
    var table = document.createElement('TABLE');
    table.border='1';

    var tableHead = document.createElement('THEAD');
    table.appendChild(tableHead);

    if (type == 'input') {
        var th = document.createElement('TH');
        tableHead.appendChild(th);
        th.appendChild(document.createTextNode("Parameter"));
        var th = document.createElement('TH');
        tableHead.appendChild(th);
        th.appendChild(document.createTextNode("Change effect"));
        var th = document.createElement('TH');
        tableHead.appendChild(th);
        th.appendChild(document.createTextNode("x-axis"));
        var th = document.createElement('TH');
        tableHead.appendChild(th);
        th.appendChild(document.createTextNode("y-axis"));
    } else if (type == 'output') {
        var th = document.createElement('TH');
        tableHead.appendChild(th);
        th.appendChild(document.createTextNode("Variable"));
        var th = document.createElement('TH');
        tableHead.appendChild(th);
        th.appendChild(document.createTextNode("Monotonicity"));
        var th = document.createElement('TH');
        tableHead.appendChild(th);
        th.appendChild(document.createTextNode("z-axis"));
    }

    var tableBody = document.createElement('TBODY');
    table.appendChild(tableBody);

    for (var i=0; i<n_var; i++){
        var tr = document.createElement('TR');
        tableBody.appendChild(tr);

        // labels
        var td = document.createElement('TD');
        if (type == 'input') {
            td.appendChild(document.createTextNode("x"+(i+1)));
        } else if (type == 'output') {
            td.appendChild(document.createTextNode("f"+(i+1)));
        }
        td.width='25';
        tr.appendChild(td);
        
        // numeric selectors
        var td = document.createElement('TD');
        td.width='75';
        td.style="text-align:center";

        var inputbox = document.createElement('input');
        inputbox.type = "number";
        inputbox.name = "name";
        inputbox.value = 0;
        inputbox.min=-1
        inputbox.max=1
        inputbox.step=1
        inputbox.id = "id";
        td.appendChild(inputbox)
        tr.appendChild(td);
        
        // plot selectors
        if (type == 'input') {
            for (var j=0; j<2; j++){
                var td = document.createElement('TD');
                td.width='75';
                td.style="text-align:center";

                var radioDiv = document.createElement('div');
                radioDiv.className = 'radio';

                var inputbox = document.createElement('input');
                inputbox.type = "radio";
                inputbox.name = "axis-"+(j+1);
                inputbox.id = "r"+(i+1)+(j+1);

                radioDiv.appendChild(inputbox)
            
                td.appendChild(radioDiv)
                tr.appendChild(td);
            }
        } else if (type == 'output') {
            for (var j=0; j<1; j++){
                var td = document.createElement('TD');
                td.width='75';
                td.style="text-align:center";

                var radioDiv = document.createElement('div');
                radioDiv.className = 'radio';

                var inputbox = document.createElement('input');
                inputbox.type = "radio";
                inputbox.name = "z-axis";
                inputbox.id = "c"+(i+1);

                radioDiv.appendChild(inputbox)
            
                td.appendChild(radioDiv)
                tr.appendChild(td);
            } 
        }

    }
    myTableDiv.appendChild(table);
    
}

function addJacobian(nrows, ncols) {

    console.log(nrows)
    console.log(ncols)
    var myTableDiv = document.getElementById("JacobianTable");
        
    var table = document.createElement('TABLE');
    table.border='1';

    var tableHead = document.createElement('THEAD');
    table.appendChild(tableHead);

    var th = document.createElement('TH');
    tableHead.appendChild(th);
    for (var j=0; j<ncols; j++){
        var th = document.createElement('TH');
        tableHead.appendChild(th);
        th.appendChild(document.createTextNode("f"+(j+1)));
    }

    var tableBody = document.createElement('TBODY');
    table.appendChild(tableBody);

    for (var i=0; i<nrows; i++){
        var tr = document.createElement('TR');
        tableBody.appendChild(tr);
        var td = document.createElement('TD');
        td.appendChild(document.createTextNode("x"+(i+1)));
        td.width='25';
        tr.appendChild(td);
        for (var j=0; j<ncols; j++){
            
            var td = document.createElement('TD');
            td.width='75';

            var checkbox = document.createElement('input');
            checkbox.type = "checkbox";
            checkbox.name = "name";
            checkbox.value = "value";
            checkbox.id = "id";
            td.appendChild(checkbox)
            tr.appendChild(td);
        }
    }
    myTableDiv.appendChild(table);
    
}
 
function load() {
    
    console.log("Page load finished");
 
}