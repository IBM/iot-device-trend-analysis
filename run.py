# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask, jsonify, render_template, json, Response, request
import os
import metrics_tracker_client
import dataset
import plotdata


#create flask application
app = Flask(__name__)

@app.route('/')
def Run():
    """
    Load the site page
    """
    return render_template('index.html')


@app.route('/deviceperday')
def Device_data_per_day():
    """
    Load devicePerDay page
    """
    return render_template('devicePerDay.html')


@app.route('/deviceacrossdays')
def Device_data_across_days():
    """
    Load deviceAcrossDays page
    """
    return render_template('deviceAcrossDays.html')


@app.route('/hourlyStatsTrends')
def Hourly_stats_trends():
    """
    Load hourlyStatsTrends page
    """
    return render_template('hourlyStatsTrends.html')


@app.route('/devicecorrelationanalysis')
def Device_correlation_analysis():
    """
    Load deviceCorrelationAnalysis page
    """
    return render_template('deviceCorrelationAnalysis.html')


@app.route('/deviceStatsAcrossDays')
def Device_stats_across_days():
    """
    Load deviceStatsAcrossDays page
    """
    return render_template('deviceStatsAcrossDays.html')


@app.route('/createdataset')
def Create_dataset():
    """
    Load createDataset page
    """
    return render_template('createDataset.html')


@app.route('/api/retrieve', methods =['GET','POST'])
def Retrieve_per_day():
    """
    Post call to retrieve data for a day for a device per user input
    """
    #retrieve the json from the ajax call
    jsonFile = ''
    if request.method == 'POST':
        jsonFile = request.json
        print ("post request")

    #if jsonFile successfully posted..
    if jsonFile != '':
        # check all required arguments are present:
        if not all(arg in jsonFile for arg in ["deviceId","date"]):
            print("Missing arguments in post request")
            return json.dumps({"status":"Error", "messages":"Missing arguments"}), 422
        inputDeviceId = jsonFile["deviceId"]
        inputDate = jsonFile["date"]
        print("retreived data: " + str(inputDeviceId) + " | " + str(inputDate) )

    #get data for device fields per day
    dataArray = plotdata.Device_data_per_day(inputDeviceId, inputDate)

    #create and return the output json
    output = {"dataArray": dataArray, "deviceId": inputDeviceId, "date" : inputDate}
    return json.dumps(output)


@app.route('/api/retrieveAcrossDays', methods =['GET','POST'])
def Retrieve_across_days():
    """
    Post call to retrieve data across days for a device per user input
    """
    #retrieve the json from the ajax call
    jsonFile = ''
    if request.method == 'POST':
        jsonFile = request.json
        print ("post request")

    #if jsonFile successfully posted..
    if jsonFile != '':
        # check all required arguments are present:
        if not all(arg in jsonFile for arg in ["deviceId","startDate","endDate"]):
            print("Missing arguments in post request")
            return json.dumps({"status":"Error", "messages":"Missing arguments"}), 422
        inputDeviceId = jsonFile["deviceId"]
        inputStartDate = jsonFile["startDate"]
        inputEndDate = jsonFile["endDate"]
        print("retreived data: " + str(inputDeviceId) + " | " + str(inputStartDate) + " | " + str(inputEndDate))

    #get data for device fields across days
    dataArray = plotdata.Device_data_across_days(inputDeviceId, inputStartDate, inputEndDate)

    #create and return the output json
    output = {"dataArray": dataArray, "deviceId": inputDeviceId, "startdate" : inputStartDate, "enddate" : inputEndDate}
    return json.dumps(output)


@app.route('/api/hourlyStatsTrends', methods =['GET','POST'])
def Retrieve_hourly_stats_trends():
    """
    Post call to retrieve data across days for a device per user input with hourly stats and trends
    """
    #retrieve the json from the ajax call
    jsonFile = ''
    if request.method == 'POST':
        jsonFile = request.json
        print ("post request")

    #if jsonFile successfully posted..
    if jsonFile != '':
        # check all required arguments are present:
        if not all(arg in jsonFile for arg in ["deviceId","field","startDate","endDate"]):
            print("Missing arguments in post request")
            return json.dumps({"status":"Error", "messages":"Missing arguments"}), 422
        inputDeviceId = jsonFile["deviceId"]
        inputStartDate = jsonFile["startDate"]
        inputEndDate = jsonFile["endDate"]
        inputField = jsonFile["field"]
        print("retreived data: " + str(inputDeviceId) + " | " + str(inputField) + " | " + str(inputStartDate) + " | " + str(inputEndDate))

    #get data for device fields across days
    dataArray = plotdata.Device_data_across_days(inputDeviceId, inputStartDate, inputEndDate)

    #get hourly stats and trends for dataArray
    hourlyData = plotdata.Hourly_stats_trends(dataArray, inputField)

    #create and return the output json
    output = {"dataArray": dataArray, "hourlyData": hourlyData, "deviceId": inputDeviceId, "startdate" : inputStartDate, "enddate" : inputEndDate, "field": inputField}
    return json.dumps(output)


@app.route('/api/deviceStats', methods =['GET','POST'])
def Retrieve_device_stats():
    """
    Post call to retrieve device stats for devices
    """

    #retrieve the json from the ajax call
    json_file = ''
    if request.method == 'POST':
        json_file = request.json
        print ("post request")

    #if json_file successfully posted..
    if json_file != '':
        # check all required arguments are present:
        if not all(arg in json_file for arg in ["deviceIds","field","startDate","endDate"]):
            print("Missing arguments in post request")
            return json.dumps({"status":"Error", "messages":"Missing arguments"}), 422
        inputDeviceIds = json_file["deviceIds"]
        inputStartDate = json_file["startDate"]
        inputEndDate = json_file["endDate"]
        inputField = json_file["field"]
        print("retreived data: " + str(inputDeviceIds) + " | " + str(inputStartDate) + " | " + str(inputEndDate) + " | " + str(inputField))

    #split deviceIds from input
    deviceIds = inputDeviceIds.split(",")

    #get data for devices across days
    dataArray = plotdata.Devices_data_across_days(deviceIds, inputStartDate, inputEndDate)

    #get plot data to compare devices
    plotdataArray = plotdata.Devices_field_data(dataArray, deviceIds, inputField)

    #create and return the output json
    output = {"dataArray": dataArray, "deviceIds": deviceIds, "plotdata": plotdataArray, "startdate": inputStartDate, "enddate" : inputEndDate, "field": inputField}
    return json.dumps(output)


@app.route('/api/setDataset', methods =['GET','POST'])
def Set_dataset():
    """
    Post call to set active dataset in dataset.json
    """
    output = {}

    #retrieve the json from the ajax call
    jsonFile = ''
    if request.method == 'POST':
        jsonFile = request.json
        print ("post request")

    #if jsonFile successfully posted..
    if jsonFile != '':
        # check all required arguments are present:
        if not all(arg in jsonFile for arg in ["dataset"]):
            print("Missing arguments in post request")
            return json.dumps({"status":"Error", "messages":"Missing arguments"}), 422
        inputDataset = jsonFile["dataset"]
        print("retreived data: " + str(inputDataset)  )

    #call update datasets.json file
    return json.dumps(dataset.Set_dataset(inputDataset))


@app.route('/api/appendDataset', methods =['GET','POST'])
def Append_dataset():
    """
    Post call to append dataset.json file with user inputs
    """

    #retrieve the json from the ajax call
    jsonFile = ''
    if request.method == 'POST':
        jsonFile = request.json
        print ("post request")

    #if jsonFile successfully posted..
    if jsonFile != '':
        # check all required arguments are present:
        if not all(arg in jsonFile for arg in ["deviceIds","dates","datasetName","dbName"]):
            print("Missing arguments in post request")
            return json.dumps({"status":"Error", "messages":"Missing arguments"}), 422
        inputDeviceIds = jsonFile["deviceIds"]
        inputDates = jsonFile["dates"]
        inputDatasetName = jsonFile["datasetName"]
        inputDbName = jsonFile["dbName"]
        print("retreived data: " + str(inputDeviceIds) + " | " + str(inputDates) + " | " + str(inputDatasetName) + " | " + str(inputDbName))

    return json.dumps(dataset.Append_dataset(inputDeviceIds, inputDates, inputDatasetName, inputDbName))


@app.route('/api/getfields',methods=['GET'])
def Get_fields():
    """
    Get and return fields
    """
    #return fields array
    fields = ['connections','deviceCount','activeClients']
    return json.dumps(fields)


@app.route('/api/getdatasets',methods=['GET'])
def Get_datasets():
    """
    Get datasets name from dataset.json file
    """
    #return datasets array
    return json.dumps(dataset.Get_datasets())


@app.route('/api/getdataset',methods=['GET'])
def Get_dataset():
    """
    Get dataset name from dataset.json file
    """
    #return active dataset
    return json.dumps(dataset.Get_dataset())


@app.route('/api/getdates',methods=['GET'])
def Get_dates():
    """
    Get and return the dates from dataset
    """
    #return dates
    return json.dumps(dataset.Get_dates())

@app.route('/api/getdeviceids',methods=['GET'])
def Get_devices():
    """
    Get and return deviceIds from dataset
    """
    #return deviceIds
    return json.dumps(dataset.Get_devices())


@app.route('/api/getdbnames',methods=['GET'])
def Get_db_names():
    """
    Get and return database name initials from the Cloudant storage for dataset initialization
    """
    #return uniqueDbnames
    return json.dumps(dataset.Get_db_names())


@app.route('/api/getdbdates',methods=['GET'])
def Get_db_dates():
    """
    Get and returns dates from the Cloudant storage for dataset initialization
    """
    #return uniqueDates
    return json.dumps(dataset.Get_db_dates())


@app.route('/api/getdbdeviceids',methods=['GET'])
def Get_db_deviceids():
    """
    Get and returns dates from the Cloudant storage for dataset initialization
    """
    #retrun uniqueDeviceIds
    return json.dumps(dataset.Get_db_deviceids())


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    metrics_tracker_client.track()
    app.run(host='0.0.0.0', port=int(port))
