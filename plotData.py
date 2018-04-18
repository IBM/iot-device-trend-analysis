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

import json
import os
import time
from datetime import timedelta, date
from dotenv import load_dotenv

import dataset

from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey

#Initalize credentials to find on IBM Cloud otherwise from .env file
if 'VCAP_SERVICES' in os.environ:
    vcapServicesData = json.loads(os.environ['VCAP_SERVICES'])
    # Log the fact that we successfully found some service information.
    print("Got vcapServicesData\n")
    serviceUsername = vcapServicesData['cloudantNoSQLDB'][0]['credentials']['username']
    servicePassword = vcapServicesData['cloudantNoSQLDB'][0]['credentials']['password']
    serviceURL = vcapServicesData['cloudantNoSQLDB'][0]['credentials']['url']
else:
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    serviceUsername = os.environ.get("CLOUDANT_USERNAME")
    servicePassword = os.environ.get("CLOUDANT_PASSWORD")
    serviceURL = os.environ.get("CLOUDANT_URL")


#create cloudant client
cloudantClient = Cloudant(serviceUsername, servicePassword, url=serviceURL)


def Device_data_per_day(inputDeviceId, inputDate):
    """
    Retrieve data for a day for a device per user input
    """
    #update database name with the dataname
    databaseName = dataset.Get_database() + inputDate

    #connect to Cloudant database and retrieve data for the database
    cloudantClient.connect()
    endPoint = '{0}/{1}'.format(serviceURL, databaseName + "/_all_docs")
    params = {'include_docs': 'true'}
    response = cloudantClient.r_session.get(endPoint, params=params)
    data = response.json()

    #initalize dataArray
    dataArray = []

    #get length of rows
    rowsLength = len(data["rows"])

    #loop through data
    for x in range(0, rowsLength):

        #if device id exists
        if("deviceId" in data["rows"][x]["doc"]):
            deviceID = data["rows"][x]["doc"]["deviceId"]

            #if deivceId matches user provided device ID, append data to dataArray
            if deviceID == inputDeviceId:
                timeStamp = data["rows"][x]["doc"]["timestamp"]
                activeClients = data["rows"][x]["doc"]["data"]["activeClients"]
                deviceCount = data["rows"][x]["doc"]["data"]["deviceCount"]
                connections = data["rows"][x]["doc"]["data"]["connections"]
                jsonData = {"deviceID": deviceID, "timeStamp": timeStamp, "activeClients": activeClients, "deviceCount": deviceCount , "connections": connections}
                dataArray.append(jsonData)

    #disconnect from cloudant db
    cloudantClient.disconnect()

    #return dataArray
    return dataArray


def Device_data_across_days(inputDeviceId, inputStartDate, inputEndDate):
    """
    Retrieve data across days for a device per user input
    """

    #split the date to retrieve days, months, years
    splitStartDate = inputStartDate.split("-")
    splitEndDate = inputEndDate.split("-")

    #create date object for start and end date
    startDate = date(int(splitStartDate[0]), int(splitStartDate[1]), int(splitStartDate[2]))
    endDate = date(int(splitEndDate[0]), int(splitEndDate[1]), int(splitEndDate[2]) + 1)

    #connect to cloudant database
    cloudantClient.connect()

    #initalize dataArray
    dataArray = []

    #loop through dates
    for singleDate in daterange(startDate, endDate):

        #update database name with date
        databaseDate = singleDate.strftime("%Y-%m-%d")
        databaseName = dataset.Get_database() + databaseDate

        #connect to Cloudant database and retrieve data for the database
        endPoint = '{0}/{1}'.format(serviceURL, databaseName + "/_all_docs")
        params = {'include_docs': 'true'}
        response = cloudantClient.r_session.get(endPoint, params=params)
        data = response.json()

        #get length of rows
        rowsLength = len(data["rows"])

        #loop through data
        for x in range(0, rowsLength):

            #if device id exists
            if("deviceId" in data["rows"][x]["doc"]):
                deviceID = data["rows"][x]["doc"]["deviceId"]

                #if deivceId matches user provided device ID, append data to dataArray
                if deviceID == inputDeviceId:
                    timeStamp = data["rows"][x]["doc"]["timestamp"]
                    activeClients = data["rows"][x]["doc"]["data"]["activeClients"]
                    deviceCount = data["rows"][x]["doc"]["data"]["deviceCount"]
                    connections = data["rows"][x]["doc"]["data"]["connections"]
                    jsonData = {"deviceID": deviceID, "timeStamp": timeStamp, "activeClients": activeClients, "deviceCount": deviceCount , "connections": connections}
                    dataArray.append(jsonData)

    #disconnect from cloudant db
    cloudantClient.disconnect()

    #return dataArray
    return dataArray


def Hourly_stats_trends(dataArray, inputField):
    """
    Create hourly stats and trends for device data across days
    """

    #get length of retrieved data
    dataLength = len(dataArray)

    #initalize hourlyData
    hourlyData = []

    #loop through data for the device
    for x in range(0, dataLength):
        #get deviceID, timeStamp and field name
        timeStamp = str(dataArray[x]["timeStamp"])
        deviceId = str(dataArray[x]["deviceID"])
        field = dataArray[x][inputField]

        #split time to get hour
        timeStampSplit = timeStamp.split("T")
        day = timeStampSplit[0]
        time = timeStampSplit[1]
        timeSplit = time.split(":")
        hour = timeSplit[0]

        #get length of hourlyData
        hourlyDataLength = len(hourlyData)
        hourlyDataExists = False

        #loop through hourlyData and check if entry exists
        for j in range(0, hourlyDataLength):

            if (deviceId == hourlyData[j]["deviceID"]) and (day == hourlyData[j]["date"]) and (hour == hourlyData[j]["hour"]):
                #if exists, then update hourly fields accordingly
                hourlyData[j]["sumField"] += field
                hourlyData[j]["countEntries"] += 1

                if field > hourlyData[j]["maxField"]:
                    hourlyData[j]["maxField"] = field
                if field < hourlyData[j]["minField"]:
                    hourlyData[j]["minField"] = field

                hourlyData[j]["avgField"] = hourlyData[j]["sumField"] / hourlyData[j]["countEntries"]
                hourlyDataExists = True

        #if entry for hourly data does not exist, then create new one
        if hourlyDataExists == False:
            plotTimeStamp = day + "T" + hour + ":30:00.000Z"
            jsonData = {"deviceID": deviceId, "date": day, "hour": hour, "plotTimeStamp": plotTimeStamp, "maxField": field, "minField": field, "avgField": field, "sumField": field, "countEntries": 1, "maxSlopeLastHour": None, "minSlopeLastHour": None, "avgSlopeLastHour": None, "field": field}
            hourlyData.append(jsonData)

    #sort hourlyData per timeStamp
    sortedHourlyData = sorted(hourlyData, key=lambda k: k['plotTimeStamp'])
    sortedHourlyDataLength = len(sortedHourlyData)

    for k in range(1, sortedHourlyDataLength):
        sortedHourlyData[k]["maxSlopeLastHour"] = sortedHourlyData[k]["maxField"] - sortedHourlyData[k-1]["maxField"]
        sortedHourlyData[k]["minSlopeLastHour"] = sortedHourlyData[k]["minField"] - sortedHourlyData[k-1]["minField"]
        sortedHourlyData[k]["avgSlopeLastHour"] = sortedHourlyData[k]["avgField"] - sortedHourlyData[k-1]["avgField"]

    #return sortedHourlyData
    return sortedHourlyData


def Devices_data_across_days(deviceIds, inputStartDate, inputEndDate):
    """
    #Retrieve data across days for devices
    """
    #split the date to retrieve days, months, years
    splitStartDate = inputStartDate.split("-")
    splitEndDate = inputEndDate.split("-")

    #create date object for start and end date
    startDate = date(int(splitStartDate[0]), int(splitStartDate[1]), int(splitStartDate[2]))
    endDate = date(int(splitEndDate[0]), int(splitEndDate[1]), int(splitEndDate[2]) + 1)

    #connect to cloudant database
    cloudantClient.connect()

    #initalize dataArray
    dataArray = []

    #loop through dates
    for singleDate in daterange(startDate, endDate):

        #update database name with date
        databaseDate = singleDate.strftime("%Y-%m-%d")
        databaseName = dataset.Get_database() + databaseDate

        #connect to Cloudant database and retrieve data for the database
        endPoint = '{0}/{1}'.format(serviceURL, databaseName + "/_all_docs")
        params = {'include_docs': 'true'}
        response = cloudantClient.r_session.get(endPoint, params=params)
        data = response.json()

        #get length of rows
        rowsLength = len(data["rows"])

        #loop through data for selected devices
        for x in range(0, rowsLength):

            #if device id exists
            if("deviceId" in data["rows"][x]["doc"]):
                deviceID = data["rows"][x]["doc"]["deviceId"]

                #if deivceId matches user provided deviceIds, append data to dataArray
                if deviceID in deviceIds:
                    timeStamp = data["rows"][x]["doc"]["timestamp"]
                    activeClients = data["rows"][x]["doc"]["data"]["activeClients"]
                    deviceCount = data["rows"][x]["doc"]["data"]["deviceCount"]
                    connections = data["rows"][x]["doc"]["data"]["connections"]
                    jsonData = {"deviceID": deviceID, "timeStamp": timeStamp, "activeClients": activeClients, "deviceCount": deviceCount , "connections": connections}
                    dataArray.append(jsonData)

    #disconnect from cloudant database
    cloudantClient.disconnect()

    #return dataArray
    return dataArray


def Devices_field_data(dataArray, deviceIds, inputField):
    """
    #Retrieve device stats per device
    """

    #get length of retrieved data
    dataLength = len(dataArray)
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
    for i in range(0, dataLength):
        for j in range(0, deviceIdsLength):
            if dataArray[i]["deviceID"] == plotData[j]["deviceId"]:
                plotData[j]["fieldData"].append(dataArray[i][inputField])

    #create and return the output json
    return plotData


def daterange(startDate, endDate):
    """
    Get date range for a start and end date
    """
    for n in range(int ((endDate - startDate).days)):
        yield startDate + timedelta(n)
