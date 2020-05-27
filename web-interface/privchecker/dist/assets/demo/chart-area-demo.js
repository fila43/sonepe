// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

// Area Chart Example

var url_string = window.location.href;
var url = new URL(url_string);

var min = url.searchParams.get("min");
var max = url.searchParams.get("max");
var def = url.searchParams.get("default");
var name = url.searchParams.get("name");
var value = url.searchParams.get("value");
var help = url.searchParams.get("help");

var result = value - min;
result = Math.round(result/max*100);

document.getElementById("hname").innerHTML = name;
document.getElementById("change").innerHTML = help;
document.getElementById("piechart").innerHTML = "Your privacy percentage score";
document.getElementById("percentage").innerHTML = result+"%";

var ctx = document.getElementById("myAreaChart");
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


