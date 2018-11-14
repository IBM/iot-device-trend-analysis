var apiUrl = location.protocol + '//' + location.host + "/api/";

$(document).ready(function() {
  updateText();
});

//update interface with deviceIds, dates and fields
function updateText() {

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

  //update device ids
  $.get(apiUrl + 'getdeviceids', function(data) {
    $('.choose-deviceid select').html(function() {
      var str = '<option value="" disabled="" selected="">[choose deviceIds]</option>';
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

}

//check user input and process, generate plot
$('.get-data').click(function() {

  //get user input data
  var formDeviceIds = document.getElementById("selectDevice");
  var deviceIds = getSelectValues(formDeviceIds)
  var formFieldsId = $('.choose-fields select').find(":selected").text();
  var formStartDate = $('.select-start select').find(":selected").text();
  var formEndDate = $('.select-end select').find(":selected").text();

  //check user inputs
  if (deviceIds.includes('[choose deviceIds]')) {
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
  var inputData = '{' + '"deviceIds" : "' + deviceIds + '", ' + '"field" : "' + formFieldsId + '", ' + '"startDate" : "' + formStartDate + '", ' + '"endDate" : "' + formEndDate + '"}';

  //make ajax call to get the desired data
  $.ajax({
    type: 'POST',
    url: apiUrl + 'deviceStats',
    data: inputData,
    dataType: 'json',
    contentType: 'application/json',
    beforeSend: function() {
      //alert('Fetching....');
    },
    success: function(data) {
      //plot the returned data
      plotDeviceStats(data);
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

function plotDeviceStats(data) {

  //get the data as variables
  var deviceData = data.dataArray;
  var deviceIds = data.deviceIds;
  var startDate = data.startdate;
  var endDate = data.enddate;
  var plotData = data.plotdata;
  var field = data.field;

  //get plot data length
  var plotDataLength = plotData.length;
  var data = []

  //create traces for each deviceId
  for (var i = 0; i < plotDataLength; i++) {
    if (plotData[i].deviceId.length > 9) {
      var id = plotData[i].deviceId.substring(0, 8);
    } else {
      var id = plotData[i].deviceId;
    }
    var trace = {
      y: plotData[i].fieldData,
      type: "box",
      name: id
    };
    data.push(trace)
  }

  //add the title
  var layout = {
    title: field + " comparison from " + startDate + " to " + endDate
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

// get selected values
function getSelectValues(select) {
  var result = [];
  var options = select && select.options;
  var opt;

  for (var i = 0, iLen = options.length; i < iLen; i++) {
    opt = options[i];

    if (opt.selected) {
      result.push(opt.value || opt.text);
    }
  }
  return result;
}

//sort the objects on key
function sortByKey(array, key) {
  return array.sort(function(a, b) {
    var x = a[key];
    var y = b[key];
    return ((x > y) ? -1 : ((x < y) ? 1 : 0));
  });
}
