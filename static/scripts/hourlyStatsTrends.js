var apiUrl = location.protocol + '//' + location.host + "/api/";

$(document).ready(function() {
  updateText();
});

//update interface with deviceIds, fields and dates
function updateText() {

  //update device ids
  $.get(apiUrl + 'getdeviceids', function(data) {
    $('.choose-deviceid select').html(function() {
      var str = '<option value="" disabled="" selected="">[choose deviceId]</option>';
      //console.log("deviceids: " + data);
      var deviceIds = JSON.parse(data)
      for (var i = 0; i < deviceIds.length; i++) {
        if (deviceIds[i].length > 9) {
          var id = deviceIds[i].substring(0, 8);
        } else {
          var id = deviceIds[i];
        }
        str = str + '<option value="' + deviceIds[i] + '">' + id + '</option>';
      }
      return str;
    });
  });

  //update fields
  $.get(apiUrl + 'getfields', function(data) {
    $('.choose-fields select').html(function() {
      var str = '<option value="" disabled="" selected="">[choose field]</option>';
      var fields = JSON.parse(data);
      for (var i = 0; i < fields.length; i++) {
        str = str + '<option>' + fields[i] + '</option>';
      }
      return str;
    });
  });

  //update dates
  $.get(apiUrl + 'getdates', function(data) {
    $('.choose-date select').html(function() {
      var str = '<option value="" disabled="" selected="">[choose date]</option>';
      var dates = JSON.parse(data)
      for (var i = 0; i < dates.length; i++) {
        str = str + '<option>' + dates[i] + '</option>';
      }
      return str;
    });
  });

}

//check user input and process, generate plot
$('.get-data').click(function() {

  //get user input data
  var formDeviceId = document.getElementById("selectDevice").value;
  var formFieldsId = $('.choose-fields select').find(":selected").text();
  var formStartDate = $('.select-start select').find(":selected").text();
  var formEndDate = $('.select-end select').find(":selected").text();

  //check user inputs
  if (formDeviceId == "") {
    alert("Select a device");
    return;
  } else if (formFieldsId.includes('[choose field]')) {
    alert("Select field");
    return;
  } else if (formStartDate.includes('[choose date]')) {
    alert("Select start date");
    return;
  } else if (formEndDate.includes('[choose date]')) {
    alert("Select end date");
    return;
  } else if (formStartDate > formEndDate) {
    alert("End date must be greater than start date");
    return;
  }

  //create json data
  var inputData = '{' + '"deviceId" : "' + formDeviceId + '", ' + '"field" : "' + formFieldsId + '", ' + '"startDate" : "' + formStartDate + '", ' + '"endDate" : "' + formEndDate + '"}';

  //make ajax call to get the desired data
  $.ajax({
    type: 'POST',
    url: apiUrl + 'hourlyStatsTrends',
    data: inputData,
    dataType: 'json',
    contentType: 'application/json',
    beforeSend: function() {
      //alert('Fetching....');
    },
    success: function(data) {
      //plot the returned data
      plotHourlyStats(data);
      plotHourlyTrends(data);
    },
    error: function(jqXHR, textStatus, errorThrown) {
      //reload on error
      alert("Error: Try again")
      console.log(errorThrown);
      console.log(textStatus);
      console.log(jqXHR);

      location.reload();
    },
    complete: function() {
      //alert('Complete')
    }
  });
});

function plotHourlyStats(data) {

  //display heading
  document.getElementById('hourlyStats').style.display = "block";

  //get the data as variables
  var deviceData = data.dataArray;
  var field = data.field;

  //sort the data by timeStamp
  var sort_data_all = sortByKey(deviceData, 'timeStamp');
  var arrayLength = sort_data_all.length;

  //initialize the fields data
  var timeStampAllArray = [];
  var fieldsArray = [];

  //retrieve the fields data
  for (var i = 0; i < arrayLength; i++) {
    timeStampAllArray.push(sort_data_all[i].timeStamp)
    if (field == "activeClients") {
      fieldsArray.push(sort_data_all[i].activeClients)
    } else if (field == "deviceCount") {
      fieldsArray.push(sort_data_all[i].deviceCount)
    } else if (field == "connections") {
      fieldsArray.push(sort_data_all[i].connections)
    } else {
      console.log("field not found")
      return;
    }
  }

  //analyze hourly data
  var hourlyData = data.hourlyData;
  var deviceId = data.deviceId;
  var startDate = data.startdate;
  var endDate = data.enddate;

  //sort the data by timeStamp
  var sort_data = sortByKey(hourlyData, 'plotTimeStamp');
  var arrayLength = sort_data.length;

  //initialize the plot data
  var timeStampArray = [];
  var maxAcArray = [];
  var minAcArray = [];
  var avgAcArray = [];

  //retrieve the plot data
  for (var i = 0; i < arrayLength; i++) {
    timeStampArray.push(sort_data[i].plotTimeStamp)
    maxAcArray.push(sort_data[i].maxField)
    minAcArray.push(sort_data[i].minField)
    avgAcArray.push(sort_data[i].avgField)
  }

  //define traces
  var maxFieldTrace = {
    x: timeStampArray,
    y: maxAcArray,
    type: "scatter",
    name: "Max hourly " + field
  };
  var minFieldTrace = {
    x: timeStampArray,
    y: minAcArray,
    type: "scatter",
    name: "Min hourly " + field,
    visible: "legendonly"
  };
  var avgFieldTrace = {
    x: timeStampArray,
    y: avgAcArray,
    type: "scatter",
    name: "Avg hourly " + field,
    visible: "legendonly"
  };
  var fieldTrace = {
    x: timeStampAllArray,
    y: fieldsArray,
    type: "scatter",
    name: field,
    visible: "legendonly"
  };

  var data = [maxFieldTrace, minFieldTrace, avgFieldTrace, fieldTrace];

  //add the title
  if (deviceId.length > 9) {
    var id = deviceId.substring(0, 8);
  } else {
    var id = deviceId;
  }
  var layout = {
    title: "Device " + id + " " + field + " - Hourly Trends "
  };

  //create plot
  Plotly.newPlot('plotly_div1', data, layout)
    .then(
      function(gd) {
        Plotly.toImage(gd, {
          height: 500,
          width: 500
        })
      });
};


function plotHourlyTrends(data) {

  //display heading
  document.getElementById('hourlyTrends').style.display = "block";

  //get the hourly data
  var hourlyData = data.hourlyData;
  var deviceId = data.deviceId;
  var startDate = data.startdate;
  var endDate = data.enddate;
  var field = data.field;

  //sort the data by timeStamp
  var sort_data = sortByKey(hourlyData, 'plotTimeStamp');
  var arrayLength = sort_data.length;

  //initialize the plot data
  var timeStampArray = [];
  var maxChangeArray = [];
  var minChangeArray = [];
  var avgChangeArray = [];

  //retrieve the plot data
  for (var i = 0; i < arrayLength; i++) {
    timeStampArray.push(sort_data[i].plotTimeStamp)
    maxChangeArray.push(sort_data[i].maxSlopeLastHour)
    minChangeArray.push(sort_data[i].minSlopeLastHour)
    avgChangeArray.push(sort_data[i].avgSlopeLastHour)
  }

  //define traces
  var maxFieldTrace = {
    x: timeStampArray,
    y: maxChangeArray,
    type: "bar",
    name: "Max " + field + " Change Per Hour"
  };
  var minFieldTrace = {
    x: timeStampArray,
    y: minChangeArray,
    type: "bar",
    name: "Min " + field + " Change Per Hour",
    visible: "legendonly"
  };
  var avgFieldTrace = {
    x: timeStampArray,
    y: avgChangeArray,
    type: "bar",
    name: "Avg " + field + " Change Per Hour",
    visible: "legendonly"
  };
  var data = [maxFieldTrace, minFieldTrace, avgFieldTrace];

  //add the title
  if (deviceId.length > 9) {
    var id = deviceId.substring(0, 8);
  } else {
    var id = deviceId;
  }
  var layout = {
    title: "Device " + id + " " + field + " - Hourly Trends "
  };

  //create plot
  Plotly.newPlot('plotly_div2', data, layout)
    .then(
      function(gd) {
        Plotly.toImage(gd, {
          height: 500,
          width: 500
        })
      });
};


//sort the objects on key
function sortByKey(array, key) {
  return array.sort(function(a, b) {
    var x = a[key];
    var y = b[key];
    return ((x > y) ? -1 : ((x < y) ? 1 : 0));
  });
}
