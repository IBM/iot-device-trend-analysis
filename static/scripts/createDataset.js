var apiUrl = location.protocol + '//' + location.host + "/api/";

$(document).ready(function() {
  updateText();
});

//update interface with deviceIds, dates and database initial names
function updateText() {

  //get db names
  $.get(apiUrl + 'getdbnames', function(data) {
    $('.choose-dbname select').html(function() {
      var str = '<option value="" disabled="" selected="">[choose iot database initial]</option>';
      var fields = JSON.parse(data);
      for (var i = 0; i < fields.length; i++) {
        str = str + '<option>' + fields[i] + '</option>';
      }
      return str;
    });
  });


  //get db dates
  $.get(apiUrl + 'getdbdates', function(data) {
    $('.choose-dates select').html(function() {
      var str = '<option value="" disabled="" selected="">[choose dates]</option>';
      var dates = JSON.parse(data)
      for (var i = 0; i < dates.length; i++) {
          str = str + '<option value="' + dates[i] + '">' + dates[i] + '</option>';
      }
      return str;
    });
  });

  //get device ids
  $.get(apiUrl + 'getdbdeviceids', function(data) {
    $('.choose-deviceids select').html(function() {
      var str = '<option value="" disabled="" selected="">[choose deviceIds]</option>';
      var deviceIds = JSON.parse(data)
      for (var i = 0; i < deviceIds.length; i++) {
          var id = deviceIds[i];
          str = str + '<option value="' + deviceIds[i] + '">' + id + '</option>';
      }
      return str;
    });
  });

}

//check user input and call server to create dataset
$('.add-dataset').click(function() {

  //get user input data
  var formDatasetName = $('.enter-dataset input').val();
  var formDbName = $('.choose-dbname select').find(":selected").text();

  var formDeviceIds = document.getElementById("selectDevices");
  var deviceIds = getSelectValues(formDeviceIds)

  var formDates = document.getElementById("selectDates");
  var dates = getSelectValues(formDates)

  //check user inputs
  if (deviceIds.includes('[choose deviceIds]')) {
    alert("Select a device");
    return;
  } else if (dates.includes('[choose dates]')) {
    alert("Select a date");
    return;
  } else if (formDatasetName === "") {
    alert("Enter Dataset Name");
    return;
  } else if (formDbName.includes('[choose iot database initial]')) {
    alert("Select iot database name");
    return;
  }

  //create json data
  var inputData = '{' + '"deviceIds" : "' + deviceIds + '", ' + '"dates" : "' + dates + '", ' + '"datasetName" : "' + formDatasetName + '", ' + '"dbName" : "' + formDbName + '"}';

  //make ajax call to add the dataset
  $.ajax({
    type: 'POST',
    url: apiUrl + 'appendDataset',
    data: inputData,
    dataType: 'json',
    contentType: 'application/json',
    beforeSend: function() {
      //alert('Fetching....');
    },
    success: function(data) {
      //sent success alert and go to home page
      alert("Created Dataset: " + data.dataset);
      location.replace("/");
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
