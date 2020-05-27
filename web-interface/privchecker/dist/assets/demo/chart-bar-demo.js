// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

var url_string = window.location.href;
var url = new URL(url_string);

var min = url.searchParams.get("min");
var max = url.searchParams.get("max");
var def = url.searchParams.get("default");
var name = url.searchParams.get("name");
var value = url.searchParams.get("value");
document.getElementById("barchart").innerHTML = "Your Privacy score";



// Bar Chart Example
var ctx = document.getElementById("myBarChart");
var myLineChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ["Min", "You", "Max", "Default"],
    datasets: [{
      label: "Privacy score",
      backgroundColor: "rgba(2,117,216,1)",

      borderColor: "rgba(2,117,216,1)",
      data: [min, value,max, def],
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
          max: Math.round(max)+1,
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


