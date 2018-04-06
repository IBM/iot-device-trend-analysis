var apiUrl = location.protocol + '//' + location.host + "/api/";

$(document).ready(function() {
    updateDropdown();
    updateDataset();
  });


//update dropdown with dataset names
function updateDropdown() {

    //update datasets dropdown
    $.get(apiUrl + 'getdatasets', function(data) {
        $('.choose-dataset select').html(function() {
            var str = '<option value="" disabled="" selected="">select dataset</option>';
            var datasets = JSON.parse(data)
            for (var i = 0; i < datasets.length; i++) {
                str = str + '<option>' + datasets[i] + '</option>';
            }
            return str;
        });
    });
}

//update active dataset name
function updateDataset() {
  $.get(apiUrl + 'getdataset', function(data) {
      $('.display-dataset').html(function() {

          var dataset = JSON.parse(data);

          var str = '<h3>Dataset: ' + dataset + '</h3>';
          return str;
      });
  });
}

//upon dataset change, call setDataset to update the active dataset
var datasetSelect = document.getElementById('dataset-dropdown');

if(datasetSelect != null)
{
  datasetSelect.onchange = function () {

      //get the dataset value from dropdown
      var formDataset = datasetSelect.options[datasetSelect.selectedIndex].value;
      var inputData = '{' + '"dataset" : "' + formDataset + '"}';

      //make ajax call to update active dataset
      $.ajax({
      type: 'POST',
      url: apiUrl + 'setDataset',
      data: inputData,
      dataType: 'json',
      contentType: 'application/json',
      beforeSend: function() {
          //alert('Fetching....');
      },
      success: function(data) {
          //upon success update the dataset on frontend
          updateDataset();
      },
      error: function(jqXHR, textStatus, errorThrown) {
          //reload on error
          alert("Error: Try again")
          console.log(errorThrown);
          console.log(textStatus);
          console.log(jqXHR);
      },
      complete: function() {
          //alert('Complete')
      }
    });

  }
}
