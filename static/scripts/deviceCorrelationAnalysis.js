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

  //update y fields
  $.get(apiUrl + 'getfields', function(data) {
    $('.choose-fieldy select').html(function() {
      var str = '<option value="" disabled="" selected="">[choose field]</option>';
      var fields = JSON.parse(data);
      for (var i = 0; i < fields.length; i++) {
        str = str + '<option>' + fields[i] + '</option>';
      }
      return str;
    });
  });

  //update x fields
  $.get(apiUrl + 'getfields', function(data) {
    $('.choose-fieldx select').html(function() {
      var str = '<option value="" disabled="" selected="">[choose field]</option>';
      var fields = JSON.parse(data);
      for (var i = 0; i < fields.length; i++) {
        str = str + '<option>' + fields[i] + '</option>';
      }
      return str;
    });
  });

}

//check user input and process, generate plot
$('.get-data').click(function() {

  //get user input data
  var formDeviceId = document.getElementById("selectDevice").value;
  var formXField = $('.choose-fieldx select').find(":selected").text();
  var formYField = $('.choose-fieldy select').find(":selected").text();
  var formStartDate = $('.select-start select').find(":selected").text();
  var formEndDate = $('.select-end select').find(":selected").text();

  //check user inputs
  if (formDeviceId == "") {
    alert("Select a device");
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
  } else if (formYField.includes('[choose field]')) {
    alert("Select field for y-axis");
    return;
  } else if (formXField.includes('[choose field]')) {
    alert("Select field for x-axis");
    return;
  }

  //create json data
  var inputData = '{' + '"deviceId" : "' + formDeviceId + '", ' + '"startDate" : "' + formStartDate + '", ' + '"endDate" : "' + formEndDate + '"}';

  //make ajax call to get the desired data
  $.ajax({
    type: 'POST',
    url: apiUrl + 'retrieveAcrossDays',
    data: inputData,
    dataType: 'json',
    contentType: 'application/json',
    beforeSend: function() {
      //alert('Fetching....');
    },
    success: function(data) {
      //plot the returned data
      plotCorrelation(data);
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

function plotCorrelation(data) {

  //get the x and y fields
  var formXField = $('.choose-fieldx select').find(":selected").text();
  var formYField = $('.choose-fieldy select').find(":selected").text();

  //get the data as variables
  var deviceData = data.dataArray;
  var deviceId = data.deviceId;
  var startDate = data.startdate;
  var endDate = data.enddate;

  //sort the data by timeStamp
  var sort_data = sortByKey(deviceData, 'timeStamp');
  var arrayLength = sort_data.length;

  //initialize the plot arrays
  var timeStampArray = [];
  var xArray = [];
  var yArray = [];

  //retrieve the data
  for (var i = 0; i < arrayLength; i++) {
    timeStampArray.push(sort_data[i].timeStamp)

    //get x field data
    if (formXField == "activeClients") {
      xArray.push(sort_data[i].activeClients)
    } else if (formXField == "deviceCount") {
      xArray.push(sort_data[i].deviceCount)
    } else if (formXField == "connections") {
      xArray.push(sort_data[i].connections)
    } else {
      console.log("field not found")
      return;
    }

    //get y field data
    if (formYField == "activeClients") {
      yArray.push(sort_data[i].activeClients)
    } else if (formYField == "deviceCount") {
      yArray.push(sort_data[i].deviceCount)
    } else if (formYField == "connections") {
      yArray.push(sort_data[i].connections)
    } else {
      console.log("field not found")
      return;
    }
  }

  //define trace
  var corrTrace = {
    x: xArray,
    y: yArray,
    type: "scatter",
    mode: 'markers',
    name: formYField + " vs " + formXField,
    showlegend: true
  };
  var data = [corrTrace];

  //add the title
  if (deviceId.length > 9) {
    var id = deviceId.substring(0, 8);
  } else {
    var id = deviceId;
  }
  var layout = {
    title: "Device " + id + " from " + startDate + " to " + endDate,
    yaxis: {
      title: formYField
    },
    xaxis: {
      title: formXField
    }
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

//sort the objects on key
function sortByKey(array, key) {
  return array.sort(function(a, b) {
    var x = a[key];
    var y = b[key];
    return ((x > y) ? -1 : ((x < y) ? 1 : 0));
  });

}
