var apiUrl = location.protocol + '//' + location.host + "/api/";

$(document).ready(function() {
  updateText();
});

//update interface with deviceIds and dates
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
      //console.log("dates: " + data);
      var dates = JSON.parse(data)
      for (var i = 0; i < dates.length; i++) {
        str = str + '<option>' + dates[i] + '</option>';
      }
      //console.log("str: " + str)
      return str;
    });
  });
}

//check user input and process, generate plot
$('.get-data').click(function() {

  //get user input data
  var formDeviceId = document.getElementById("selectDevice").value;
  var formDate = $('.choose-date select').find(":selected").text();

  //check user inputs
  if (formDeviceId == "") {
    alert("Select a device");
    return;
  } else if (formDate.includes('[choose date]')) {
    alert("Select a date");
    return;
  }

  //create json data
  var inputData = '{' + '"deviceId" : "' + formDeviceId + '", ' + '"date" : "' + formDate + '"}';

  //make ajax call to get the desired data
  $.ajax({
    type: 'POST',
    url: apiUrl + 'retrieve',
    data: inputData,
    dataType: 'json',
    contentType: 'application/json',
    beforeSend: function() {
      //alert('Fetching....');
    },
    success: function(data) {
      //plot the returned data
      plotPerDay(data);
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

function plotPerDay(data) {

  //get the data as variables
  var deviceData = data.dataArray
  var deviceId = data.deviceId
  var date = data.date

  //sort the data by timeStamp
  var sort_data = sortByKey(deviceData, 'timeStamp');
  var arrayLength = sort_data.length;

  //initialize the fields data
  var timeStampArray = [];
  var activeClientsArray = [];
  var deviceCountArray = [];
  var connectionsArray = [];

  //retrieve the fields data
  for (var i = 0; i < arrayLength; i++) {
    timeStampArray.push(sort_data[i].timeStamp)
    activeClientsArray.push(sort_data[i].activeClients)
    deviceCountArray.push(sort_data[i].deviceCount)
    connectionsArray.push(sort_data[i].connections)
  }

  //define traces
  var activeClientsTrace = {
    x: timeStampArray,
    y: activeClientsArray,
    type: "scatter",
    name: "activeClients"
  };
  var deviceCountTrace = {
    x: timeStampArray,
    y: deviceCountArray,
    type: "scatter",
    name: "deviceCount",
    visible: "legendonly"
  };
  var connectionsTrace = {
    x: timeStampArray,
    y: connectionsArray,
    type: "scatter",
    name: "connections",
    visible: "legendonly"
  };
  var data = [activeClientsTrace, deviceCountTrace, connectionsTrace];

  //add the title
  if (deviceId.length > 9) {
    var id = deviceId.substring(0, 8);
  } else {
    var id = deviceId;
  }
  var layout = {
    title: "Device " + id + " on " + date
  };

  //create plot
  Plotly.newPlot(
      'plotly_div', data, layout)
    .then(
      function(gd) {
        Plotly.toImage(gd, {
            height: 500,
            width: 500
          })
          .then(
            function(url) {
              return Plotly.toImage(gd, {
                format: 'jpeg',
                height: 600,
                width: 600
              });
            }
          )
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
