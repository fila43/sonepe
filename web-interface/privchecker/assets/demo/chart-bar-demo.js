// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

var url_string = window.location.href;
var url = new URL(url_string);

function generate_extern_items(data){
    var result="";
    for (var x= 0; x<data.length;x++){
        result = result+`<div title"" class="card-footer d-flex align-items-center justify-content-between"><a class="small text-white stretched-link" id="change">`+data[x]+'</a></div>';
    }
    return result;
}

var networks = data.intern;
    $("#osns").append(`
                        <ol class="breadcrumb mb-4">
                            <li class="breadcrumb-item active osn_name">`+"Your public informations"+`</li>
                        </ol>
                        <div class="row">
                            
                            
                            <div class="col-xl-3 col-md-6">
                                <div class="card bg-danger text-white mb-4" style="
    width: 206%;
">
                                    <div class="card-body">Publicly shared information accessed without any registration into social networks</div>

                                   

   `+generate_extern_items(data.extern_data)+`


                                </div>
                            </div>
                            <div class="col-xl-3 col-md-6">
                                <div class="card bg-danger text-white mb-4" style="
    display: none;
">
                                    <div class="card-body">Danger setting</div>
                                    <div class="card-footer d-flex align-items-center justify-content-between">
                                        <a class="small text-white stretched-link" href="#">View Details</a>
                                        <div class="small text-white"><svg class="svg-inline--fa fa-angle-right fa-w-8" aria-hidden="true" focusable="false" data-prefix="fas" data-icon="angle-right" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 512" data-fa-i2svg=""><path fill="currentColor" d="M224.3 273l-136 136c-9.4 9.4-24.6 9.4-33.9 0l-22.6-22.6c-9.4-9.4-9.4-24.6 0-33.9l96.4-96.4-96.4-96.4c-9.4-9.4-9.4-24.6 0-33.9L54.3 103c9.4-9.4 24.6-9.4 33.9 0l136 136c9.5 9.4 9.5 24.6.1 34z"></path></svg><!-- <i class="fas fa-angle-right"></i> --></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="row">
                            
                            
                            <div class="col-xl-3 col-md-6">
                                <div id="user_type" class="card text-white mb-4" style="
    width: 206%;
">
                                    <div class="card-body" id="user"></div>

                                   



                                </div>
                            </div>
                            <div class="col-xl-3 col-md-6">
                                <div class="card bg-danger text-white mb-4" style="
    display: none;
">
                                    <div class="card-body">Danger setting</div>
                                    <div class="card-footer d-flex align-items-center justify-content-between">
                                        <a class="small text-white stretched-link" href="#">View Details</a>
                                        <div class="small text-white"><svg class="svg-inline--fa fa-angle-right fa-w-8" aria-hidden="true" focusable="false" data-prefix="fas" data-icon="angle-right" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 512" data-fa-i2svg=""><path fill="currentColor" d="M224.3 273l-136 136c-9.4 9.4-24.6 9.4-33.9 0l-22.6-22.6c-9.4-9.4-9.4-24.6 0-33.9l96.4-96.4-96.4-96.4c-9.4-9.4-9.4-24.6 0-33.9L54.3 103c9.4-9.4 24.6-9.4 33.9 0l136 136c9.5 9.4 9.5 24.6.1 34z"></path></svg><!-- <i class="fas fa-angle-right"></i> --></div>
                                    </div>
                                </div>
                            </div>
                        </div>




                        <div class="row">
                            <div class="col-xl-6">
                                <div class="card mb-4">
                                    <div class="card-header" id="piechart">Your privacy percentage score</div>
                                    <div class="card-body"><div class="chartjs-size-monitor"><div class="chartjs-size-monitor-expand"><div class=""></div></div><div class="chartjs-size-monitor-shrink"><div class=""></div></div></div><div class="chartjs-size-monitor"><div class="chartjs-size-monitor-expand"><div class=""></div></div><div class="chartjs-size-monitor-shrink"><div class=""></div></div></div><div class="chartjs-size-monitor"><div class="chartjs-size-monitor-expand"><div class=""></div></div><div class="chartjs-size-monitor-shrink"><div class=""></div></div></div>
<p id="`+"extern"+`_percentage" style="
    font-size: 1.5em;
    position: absolute;
    margin-left: 44%;
    margin-top: 19%;
">NaN%</p>
                                        <canvas id="`+"extern"+`_percentagechart" width="762" height="304" style="display: block; width: 762px; height: 304px;" class="chartjs-render-monitor"></canvas></div>
                                </div>
                            </div>
                            <div class="col-xl-6">
                                <div class="card mb-4">
                                    <div class="card-header" id="barchart">Your Privacy score</div>
                                    <div class="card-body"><div class="chartjs-size-monitor"><div class="chartjs-size-monitor-expand"><div class=""></div></div><div class="chartjs-size-monitor-shrink"><div class=""></div></div></div><div class="chartjs-size-monitor"><div class="chartjs-size-monitor-expand"><div class=""></div></div><div class="chartjs-size-monitor-shrink"><div class=""></div></div></div><div class="chartjs-size-monitor"><div class="chartjs-size-monitor-expand"><div class=""></div></div><div class="chartjs-size-monitor-shrink"><div class=""></div></div></div><canvas id="`+"extern"+`_barchart" width="762" height="304" class="chartjs-render-monitor" style="display: block; width: 762px; height: 304px;"></canvas></div>
                                </div>
                            </div>
                        </div>
                        `);

// Bar Chart Example
var ctx = document.getElementById("extern_barchart");
var myLineChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ["Min", "You", "Max"],
    datasets: [{
      label: "Privacy score",
      backgroundColor: "rgba(2,117,216,1)",

      borderColor: "rgba(2,117,216,1)",
      data: [data.extern_min, data.extern,data.extern_max],
    }],
  },
  options: {
    scales: {
      xAxes: [{
        time: {
          unit: 'month'
        },
        gridLines: {
          display: false
        },
        ticks: {
          maxTicksLimit: 6
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: Math.round(data.extern_max)+1,
          maxTicksLimit:5 
	},
        gridLines: {
          display: true
        }
      }],
    },
    legend: {
      display: false
    }
  }
});



var result = data.extern - data.extern_min;
 result = Math.round(result/(data.extern_max-data.extern_min)*100);
var user_type = "" 
var user = ""

if (result < 16){
	user_type = "Defensive user";
	user = "bg-success";
}
else if	(result >= 16 && result < 84){
	user_type = "Majority user";
	user = "bg-warning";
}else {
	user_type = "Careless user";
	user = "bg-danger";
} 


document.getElementById("user").innerHTML = user_type;

document.getElementById("user_type").classList.add(user);

document.getElementById("extern_percentage").innerHTML = result+"%";
 
  var ctx = document.getElementById("extern_percentagechart");
  var myLineChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [result,100-result],
          "backgroundColor":["rgb(255,0,0)","rgb(255, 255, 255)",]
      }],
  labels: [
          'Percentage privacy score',
          ''
      ]
    },
    options: []
  
  });

for (var i =0; i<networks.length;i++){
var result = networks[i].result - networks[i].min;
result = Math.round(result/(networks[i].max-networks[i].min)*100);
var user_type = "" 
var user = ""

if (result < 16){
	user_type = "Defensive user";
	user = "bg-success";
}
else if	(result >= 16 && result < 84){
	user_type = "Majority user";
	user = "bg-warning";
}else {
	user_type = "Careless user";
	user = "bg-danger";
} 





$("#osns").append(`
                        <ol class="breadcrumb mb-4">
                            <li class="breadcrumb-item active osn_name">`+networks[i].name+`</li>
                        </ol>
                        <div class="row">
                            
                            
                            <div class="col-xl-3 col-md-6">
                                <div class="card bg-success text-white mb-4" style="
    width: 206%;
">
                                    <div class="card-body">Recommended to change</div>
                                    <div class="card-footer d-flex align-items-center justify-content-between">
                                        <a class="small text-white stretched-link" id="change">`+networks[i].advices[0]+`</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-xl-3 col-md-6">
                                <div class="card bg-danger text-white mb-4" style="
    display: none;
">
                                    <div class="card-body">Danger setting</div>
                                    <div class="card-footer d-flex align-items-center justify-content-between">
                                        <a class="small text-white stretched-link" href="#">View Details</a>
                                        <div class="small text-white"><svg class="svg-inline--fa fa-angle-right fa-w-8" aria-hidden="true" focusable="false" data-prefix="fas" data-icon="angle-right" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 512" data-fa-i2svg=""><path fill="currentColor" d="M224.3 273l-136 136c-9.4 9.4-24.6 9.4-33.9 0l-22.6-22.6c-9.4-9.4-9.4-24.6 0-33.9l96.4-96.4-96.4-96.4c-9.4-9.4-9.4-24.6 0-33.9L54.3 103c9.4-9.4 24.6-9.4 33.9 0l136 136c9.5 9.4 9.5 24.6.1 34z"></path></svg><!-- <i class="fas fa-angle-right"></i> --></div>
                                    </div>
                                </div>
                            </div>
                        </div>

<div class="row">
                            
                            
                            <div class="col-xl-3 col-md-6">
                                <div id="user_type_i" class="card text-white mb-4 `+user+`" style="
    width: 206%;
">
                                    <div class="card-body" id="user_i">`+user_type+`</div>

                                   

   


                                </div>
                            </div>
                            <div class="col-xl-3 col-md-6">
                                <div class="card bg-danger text-white mb-4" style="
    display: none;
">
                                    <div class="card-body">Danger setting</div>
                                    <div class="card-footer d-flex align-items-center justify-content-between">
                                        <a class="small text-white stretched-link" href="#">View Details</a>
                                        <div class="small text-white"><svg class="svg-inline--fa fa-angle-right fa-w-8" aria-hidden="true" focusable="false" data-prefix="fas" data-icon="angle-right" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 512" data-fa-i2svg=""><path fill="currentColor" d="M224.3 273l-136 136c-9.4 9.4-24.6 9.4-33.9 0l-22.6-22.6c-9.4-9.4-9.4-24.6 0-33.9l96.4-96.4-96.4-96.4c-9.4-9.4-9.4-24.6 0-33.9L54.3 103c9.4-9.4 24.6-9.4 33.9 0l136 136c9.5 9.4 9.5 24.6.1 34z"></path></svg><!-- <i class="fas fa-angle-right"></i> --></div>
                                    </div>
                                </div>
                            </div>
                        </div>


                        <div class="row">
                            <div class="col-xl-6">
                                <div class="card mb-4">
                                    <div class="card-header" id="piechart">Your privacy percentage score</div>
                                    <div class="card-body"><div class="chartjs-size-monitor"><div class="chartjs-size-monitor-expand"><div class=""></div></div><div class="chartjs-size-monitor-shrink"><div class=""></div></div></div><div class="chartjs-size-monitor"><div class="chartjs-size-monitor-expand"><div class=""></div></div><div class="chartjs-size-monitor-shrink"><div class=""></div></div></div><div class="chartjs-size-monitor"><div class="chartjs-size-monitor-expand"><div class=""></div></div><div class="chartjs-size-monitor-shrink"><div class=""></div></div></div>
<p id="`+networks[i].name+`_percentage" style="
    font-size: 1.5em;
    position: absolute;
    margin-left: 44%;
    margin-top: 19%;
">NaN%</p>
                                        <canvas id="`+networks[i].name+`_percentagechart" width="762" height="304" style="display: block; width: 762px; height: 304px;" class="chartjs-render-monitor"></canvas></div>
                                </div>
                            </div>
                            <div class="col-xl-6">
                                <div class="card mb-4">
                                    <div class="card-header" id="barchart">Your Privacy score</div>
                                    <div class="card-body"><div class="chartjs-size-monitor"><div class="chartjs-size-monitor-expand"><div class=""></div></div><div class="chartjs-size-monitor-shrink"><div class=""></div></div></div><div class="chartjs-size-monitor"><div class="chartjs-size-monitor-expand"><div class=""></div></div><div class="chartjs-size-monitor-shrink"><div class=""></div></div></div><div class="chartjs-size-monitor"><div class="chartjs-size-monitor-expand"><div class=""></div></div><div class="chartjs-size-monitor-shrink"><div class=""></div></div></div><canvas id="`+networks[i].name+`_barchart" width="762" height="304" class="chartjs-render-monitor" style="display: block; width: 762px; height: 304px;"></canvas></div>
                                </div>
                            </div>
                        </div>
                        `);


// Bar Chart Example
var ctx = document.getElementById(networks[i].name+"_barchart");
var myLineChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ["Min", "You", "Max", "Default"],
    datasets: [{
      label: "Privacy score",
      backgroundColor: "rgba(2,117,216,1)",

      borderColor: "rgba(2,117,216,1)",
      data: [networks[i].min, networks[i].result,networks[i].max, networks[i].default],
    }],
  },
  options: {
    scales: {
      xAxes: [{
        time: {
          unit: 'month'
        },
        gridLines: {
          display: false
        },
        ticks: {
          maxTicksLimit: 6
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: Math.round(networks[i].max)+1,
          maxTicksLimit:5 
	},
        gridLines: {
          display: true
        }
      }],
    },
    legend: {
      display: false
    }
  }
});



document.getElementById(networks[i].name+"_percentage").innerHTML = result+"%";



  var ctx = document.getElementById(networks[i].name+"_percentagechart");
  var myLineChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [result,100-result],
          "backgroundColor":["rgb(255,0,0)","rgb(255, 255, 255)",]
      }],
  labels: [
          'Percentage privacy score',
          ''
      ]
    },
    options: []
  
  });
}
