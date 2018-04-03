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


import os
from flask import Flask, jsonify, render_template, json, Response, request
import requests
from datetime import timedelta, date
import time
import os
from dotenv import load_dotenv

from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey

#Initalize credentials to find on IBM Cloud otherwise from .env file
if 'VCAP_SERVICES' in os.environ:
    vcap_servicesData = json.loads(os.environ['VCAP_SERVICES'])
    # Log the fact that we successfully found some service information.
    print("Got vcap_servicesData\n")
    serviceUsername = vcap_servicesData['cloudantNoSQLDB'][0]['credentials']['username']
    servicePassword = vcap_servicesData['cloudantNoSQLDB'][0]['credentials']['password']
    serviceURL = vcap_servicesData['cloudantNoSQLDB'][0]['credentials']['url']
else:
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    serviceUsername = os.environ.get("CLOUDANT_USERNAME")
    servicePassword = os.environ.get("CLOUDANT_PASSWORD")
    serviceURL = os.environ.get("CLOUDANT_URL")


#connect to cloudant
cloudantClient = Cloudant(serviceUsername, servicePassword, url=serviceURL)

#hard coded database name
iotDatabaseName = "iotp_nmghmm_default_"

#hard coded deviceIds
deviceIds = ['19ca0a0b6','02e356e3a','2eeae108d','c270d3f23','19c94a94f',
                '38a42a88e','076814d5e','7c45d2861','a0c91d0f8','f788dc541']

#hard coded dates
dates = ['2018-01-16','2018-01-17','2018-01-18','2018-01-19','2018-01-20',
            '2018-01-21','2018-01-22','2018-01-23','2018-01-24','2018-01-25']

#fields
fields = ['connections','deviceCount','activeClients']

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

@app.route('/api/getdates',methods=['GET'])
def Get_dates():
    """
    Collect and return the dates
    """
    return json.dumps(dates)

@app.route('/api/getdeviceids',methods=['GET'])
def Get_devices():
    """
    Collect and return deviceIds
    """
    return json.dumps(deviceIds)

@app.route('/api/getfields',methods=['GET'])
def Get_fields():
    """
    Collect and return fields
    """
    return json.dumps(fields)


@app.route('/api/retrieve', methods =['GET','POST'])
def Retrieve():
    """
    Retrieve data for a day for a device per user input
    """
    output = {}

    #retrieve the json from the ajax call
    json_file = ''
    if request.method == 'POST':
        json_file = request.json
        print ("post request")

    #if json_file successfully posted..
    if json_file != '':
        # check all required arguments are present:
        if not all(arg in json_file for arg in ["deviceId","date"]):
            print("Missing arguments in post request")
            return json.dumps({"status":"Error", "messages":"Missing arguments"}), 422
        inputDeviceId = json_file["deviceId"]
        inputDate = json_file["date"]
        print("retreived data: " + str(inputDeviceId) + " | " + str(inputDate) )

    #update database name with the dataname
    databaseName = iotDatabaseName + inputDate

    #connect to Cloudant database and retrieve data for the database
    cloudantClient.connect()
    end_point = '{0}/{1}'.format(serviceURL, databaseName + "/_all_docs")
    params = {'include_docs': 'true'}
    response = cloudantClient.r_session.get(end_point, params=params)
    data = response.json()

    #initalize data_array
    data_array = []

    #get length of rows
    rows_length = len(data["rows"])

    #loop through data
    for x in range(0, rows_length):

        if("deviceId" in data["rows"][x]["doc"]):
            deviceID = data["rows"][x]["doc"]["deviceId"]
            timeStamp = data["rows"][x]["doc"]["timestamp"]
            activeClients = data["rows"][x]["doc"]["data"]["activeClients"]
            deviceCount = data["rows"][x]["doc"]["data"]["deviceCount"]
            connections = data["rows"][x]["doc"]["data"]["connections"]

        #if deivceId matches user provided device ID, append data to data_array
        if deviceID == inputDeviceId:
            json_data = {"deviceID": deviceID, "timeStamp": timeStamp, "activeClients": activeClients, "deviceCount": deviceCount , "connections": connections}
            data_array.append(json_data)

    #create the output json
    output = {"dataArray": data_array, "deviceId": inputDeviceId, "date" : inputDate}
    cloudantClient.disconnect()

    #return output
    return json.dumps(output)


@app.route('/api/retrieveAcrossDays', methods =['GET','POST'])
def RetrieveAcrossDays():
    """
    Retrieve data across days for a device per user input
    """
    output = {}

    #retrieve the json from the ajax call
    json_file = ''
    if request.method == 'POST':
        json_file = request.json
        print ("post request")

    #if json_file successfully posted..
    if json_file != '':
        # check all required arguments are present:
        if not all(arg in json_file for arg in ["deviceId","startDate","endDate"]):
            print("Missing arguments in post request")
            return json.dumps({"status":"Error", "messages":"Missing arguments"}), 422
        inputDeviceId = json_file["deviceId"]
        inputStartDate = json_file["startDate"]
        inputEndDate = json_file["endDate"]
        print("retreived data: " + str(inputDeviceId) + " | " + str(inputStartDate) + " | " + str(inputEndDate))

    #split the date to retrieve days, months, years
    splitStartDate = inputStartDate.split("-")
    splitEndDate = inputEndDate.split("-")

    #create date object for start and end date
    start_date = date(int(splitStartDate[0]), int(splitStartDate[1]), int(splitStartDate[2]))
    end_date = date(int(splitEndDate[0]), int(splitEndDate[1]), int(splitEndDate[2]) + 1)

    #connect to cloudant database
    cloudantClient.connect()

    #initalize data_array
    data_array = []

    #loop through dates
    for single_date in daterange(start_date, end_date):

        #update database name with date
        database_date = single_date.strftime("%Y-%m-%d")
        databaseName = iotDatabaseName + database_date

        #connect to Cloudant database and retrieve data for the database
        end_point = '{0}/{1}'.format(serviceURL, databaseName + "/_all_docs")
        params = {'include_docs': 'true'}
        response = cloudantClient.r_session.get(end_point, params=params)
        data = response.json()

        #get length of rows
        rows_length = len(data["rows"])

        #loop through data
        for x in range(0, rows_length):

            if("deviceId" in data["rows"][x]["doc"]):
                deviceID = data["rows"][x]["doc"]["deviceId"]
                timeStamp = data["rows"][x]["doc"]["timestamp"]
                activeClients = data["rows"][x]["doc"]["data"]["activeClients"]
                deviceCount = data["rows"][x]["doc"]["data"]["deviceCount"]
                connections = data["rows"][x]["doc"]["data"]["connections"]

            #if deivceId matches user provided device ID, append data to data_array
            if deviceID == inputDeviceId:
                json_data = {"deviceID": deviceID, "timeStamp": timeStamp, "activeClients": activeClients, "deviceCount": deviceCount , "connections": connections}
                data_array.append(json_data)

    #disconnect from cloudant db
    cloudantClient.disconnect()

    #create and return the output json
    output = {"dataArray": data_array, "deviceId": inputDeviceId, "startdate" : inputStartDate, "enddate" : inputEndDate}
    return json.dumps(output)


@app.route('/api/hourlyStatsTrends', methods =['GET','POST'])
def HourlyStatsTrends():
    """
    Retrieve data across days for a device per user input with hourly stats and trends
    """
    output = {}

    #retrieve the json from the ajax call
    json_file = ''
    if request.method == 'POST':
        json_file = request.json
        print ("post request")

    #if json_file successfully posted..
    if json_file != '':
        # check all required arguments are present:
        if not all(arg in json_file for arg in ["deviceId","field","startDate","endDate"]):
            print("Missing arguments in post request")
            return json.dumps({"status":"Error", "messages":"Missing arguments"}), 422
        inputDeviceId = json_file["deviceId"]
        inputStartDate = json_file["startDate"]
        inputEndDate = json_file["endDate"]
        inputField = json_file["field"]
        print("retreived data: " + str(inputDeviceId) + " | " + str(inputField) + " | " + str(inputStartDate) + " | " + str(inputEndDate))

    #split the date to retrieve days, months, years
    splitStartDate = inputStartDate.split("-")
    splitEndDate = inputEndDate.split("-")

    #create date object for start and end date
    start_date = date(int(splitStartDate[0]), int(splitStartDate[1]), int(splitStartDate[2]))
    end_date = date(int(splitEndDate[0]), int(splitEndDate[1]), int(splitEndDate[2]) + 1)

    #connect to cloudant database
    cloudantClient.connect()

    #initalize data_array
    data_array = []

    #loop through dates
    for single_date in daterange(start_date, end_date):

        #update database name with date
        database_date = single_date.strftime("%Y-%m-%d")
        databaseName = iotDatabaseName + database_date

        #connect to Cloudant database and retrieve data for the database
        end_point = '{0}/{1}'.format(serviceURL, databaseName + "/_all_docs")
        params = {'include_docs': 'true'}
        response = cloudantClient.r_session.get(end_point, params=params)
        data = response.json()

        #get length of rows
        rows_length = len(data["rows"])

        #loop through data
        for x in range(0, rows_length):

            if("deviceId" in data["rows"][x]["doc"]):
                deviceID = data["rows"][x]["doc"]["deviceId"]
                timeStamp = data["rows"][x]["doc"]["timestamp"]
                activeClients = data["rows"][x]["doc"]["data"]["activeClients"]
                deviceCount = data["rows"][x]["doc"]["data"]["deviceCount"]
                connections = data["rows"][x]["doc"]["data"]["connections"]

            #if deivceId matches user provided device ID, append data to data_array
            if deviceID == inputDeviceId:
                json_data = {"deviceID": deviceID, "timeStamp": timeStamp, "activeClients": activeClients, "deviceCount": deviceCount , "connections": connections}
                data_array.append(json_data)

    #disconnect from cloudant database
    cloudantClient.disconnect()

    #get length of retrieved data
    data_length = len(data_array)

    #initalize hourlyData
    hourlyData = []

    #loop through data for the device
    for x in range(0, data_length):
        #get deviceID, timeStamp and field name
        timeStamp = str(data_array[x]["timeStamp"])
        deviceId = str(data_array[x]["deviceID"])
        field = data_array[x][inputField]

        #split time to get hour
        timeStampSplit = timeStamp.split("T")
        day = timeStampSplit[0]
        time = timeStampSplit[1]
        timeSplit = time.split(":")
        hour = timeSplit[0]

        #get length of hourlyData
        hourlyData_length = len(hourlyData)
        hourlyData_exists = False

        #loop through hourlyData and check if entry exists
        for j in range(0, hourlyData_length):

            if (deviceId == hourlyData[j]["deviceID"]) and (day == hourlyData[j]["date"]) and (hour == hourlyData[j]["hour"]):
                #if exists, then update hourly fields accordingly
                hourlyData[j]["sumField"] += field
                hourlyData[j]["countEntries"] += 1

                if field > hourlyData[j]["maxField"]:
                    hourlyData[j]["maxField"] = field
                if field < hourlyData[j]["minField"]:
                    hourlyData[j]["minField"] = field

                hourlyData[j]["avgField"] = hourlyData[j]["sumField"] / hourlyData[j]["countEntries"]
                hourlyData_exists = True

        #if entry for hourly data does not exist, then create new one
        if hourlyData_exists == False:
            plotTimeStamp = day + "T" + hour + ":30:00.000Z"
            json_data = {"deviceID": deviceId, "date": day, "hour": hour, "plotTimeStamp": plotTimeStamp, "maxField": field, "minField": field, "avgField": field, "sumField": field, "countEntries": 1, "maxSlopeLastHour": None, "minSlopeLastHour": None, "avgSlopeLastHour": None, "field": field}
            hourlyData.append(json_data)

    #sort hourlyData per timeStamp
    sortedHourlyData = sorted(hourlyData, key=lambda k: k['plotTimeStamp'])
    sortedHourlyData_length = len(sortedHourlyData)

    for k in range(1, sortedHourlyData_length):
        sortedHourlyData[k]["maxSlopeLastHour"] = sortedHourlyData[k]["maxField"] - sortedHourlyData[k-1]["maxField"]
        sortedHourlyData[k]["minSlopeLastHour"] = sortedHourlyData[k]["minField"] - sortedHourlyData[k-1]["minField"]
        sortedHourlyData[k]["avgSlopeLastHour"] = sortedHourlyData[k]["avgField"] - sortedHourlyData[k-1]["avgField"]

    #create and return the output json
    output = {"dataArray": data_array, "hourlyData": sortedHourlyData, "deviceId": inputDeviceId, "startdate" : inputStartDate, "enddate" : inputEndDate, "field": inputField}
    return json.dumps(output)


@app.route('/api/deviceStats', methods =['GET','POST'])
def DeviceStats():
    """
    Retrieve device stats for devices
    """
    output = {}

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
        print("retreived data: " + str(inputDeviceIds) + " | " + str(inputStartDate) + " | " + str(inputEndDate))

    #split the date to retrieve days, months, years, split deviceIds from input
    splitStartDate = inputStartDate.split("-")
    splitEndDate = inputEndDate.split("-")
    deviceIds = inputDeviceIds.split(",")

    #create date object for start and end date
    start_date = date(int(splitStartDate[0]), int(splitStartDate[1]), int(splitStartDate[2]))
    end_date = date(int(splitEndDate[0]), int(splitEndDate[1]), int(splitEndDate[2]) + 1)

    #connect to cloudant database
    cloudantClient.connect()

    #initalize data_array
    data_array = []

    #loop through dates
    for single_date in daterange(start_date, end_date):

        #update database name with date
        database_date = single_date.strftime("%Y-%m-%d")
        databaseName = iotDatabaseName + database_date

        #connect to Cloudant database and retrieve data for the database
        end_point = '{0}/{1}'.format(serviceURL, databaseName + "/_all_docs")
        params = {'include_docs': 'true'}
        response = cloudantClient.r_session.get(end_point, params=params)
        data = response.json()

        #get length of rows
        rows_length = len(data["rows"])

        #loop through data for selected devices
        for x in range(0, rows_length):

            if("deviceId" in data["rows"][x]["doc"]):
                deviceID = data["rows"][x]["doc"]["deviceId"]
                timeStamp = data["rows"][x]["doc"]["timestamp"]
                activeClients = data["rows"][x]["doc"]["data"]["activeClients"]
                deviceCount = data["rows"][x]["doc"]["data"]["deviceCount"]
                connections = data["rows"][x]["doc"]["data"]["connections"]

            #if deivceId matches user provided deviceIds, append data to data_array
            if deviceID in deviceIds:
                json_data = {"deviceID": deviceID, "timeStamp": timeStamp, "activeClients": activeClients, "deviceCount": deviceCount , "connections": connections}
                data_array.append(json_data)

    #disconnect from cloudant database
    cloudantClient.disconnect()

    #get length of retrieved data
    data_length = len(data_array)
    deviceIdsLength = len(deviceIds)

    #initalize plotData
    plotData = []

    #loop through deviceIds and append plotData
    for j in range(0, deviceIdsLength):
        deviceData = {}
        deviceData["deviceId"] = deviceIds[j]
        deviceData["fieldData"] = []
        plotData.append(deviceData)

    #added the selected field's data to plotData
    for i in range(0, data_length):
        for j in range(0, deviceIdsLength):
            if data_array[i]["deviceID"] == plotData[j]["deviceId"]:
                plotData[j]["fieldData"].append(data_array[i][inputField])

    #create and return the output json
    output = {"dataArray": data_array, "deviceIds": deviceIds, "plotData": plotData, "startdate": inputStartDate, "enddate" : inputEndDate, "field": inputField}
    return json.dumps(output)


def daterange(start_date, end_date):
    """
    Get date range for a start and end date
    """
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
