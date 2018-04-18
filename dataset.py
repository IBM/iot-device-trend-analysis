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
from dotenv import load_dotenv

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


def Get_datasets():
    """
    Gets datasets name from dataset.json file
    """

    #initialize datasets array
    datasets = []

    #read json from datasets.json file
    with open('datasets.json', 'r') as data_file:
        data = json.load(data_file)
        data_file.close()

    #get number of datasets in file
    datasetsLength = len(data["datasets"])

    #loop through datasets and add to array
    for x in range(0, datasetsLength):
        if("dataset" in data["datasets"][x]):
            dataset = data["datasets"][x]["dataset"]
            datasets.append(dataset)

    #return datasets array
    return datasets


def Get_dataset():
    """
    Gets dataset name from dataset.json file
    """
    #read json from datasets.json file
    with open('datasets.json', 'r') as data_file:
        data = json.load(data_file)
        data_file.close()

    #return active dataset
    dataset = data["currentDataset"]
    return dataset


def Set_dataset(inputDataset):
    """
    Sets active dataset in dataset.json
    """

    #assign dataset from user input
    dataset = inputDataset
    output = {"dataset": dataset}

    #read json from datasets.json file
    with open('datasets.json', 'r') as data_file:
        data = json.load(data_file)
        data_file.close()

    #assigns active dataset
    data["currentDataset"] = dataset

    #updates datasets.json file
    with open('datasets.json', 'w') as outfile:
        json.dump(data, outfile)
        outfile.close()

    #return output
    return output


def Get_dates():
    """
    Collects and return the dates
    """
    #read json from datasets.json file
    with open('datasets.json', 'r') as data_file:
        data = json.load(data_file)
        data_file.close()

    #get the active dataset
    currentDataset = data["currentDataset"]

    #get the length of datasets in json
    datasetsLength = len(data["datasets"])

    #loop through datasets and get dates for the active dataset
    for x in range(0, datasetsLength):
        if("dataset" in data["datasets"][x]):
            if(data["datasets"][x]["dataset"] == currentDataset):
                dates = data["datasets"][x]["dates"]

    #return dates
    return dates


def Get_devices():
    """
    Collect and return deviceIds
    """
    #read json from datasets.json file
    with open('datasets.json', 'r') as data_file:
        data = json.load(data_file)
        data_file.close()

    #get the active dataset
    currentDataset = data["currentDataset"]

    #get the length of datasets in json
    datasetsLength = len(data["datasets"])

    #loop through datasets and get deviceIds for the active dataset
    for x in range(0, datasetsLength):
        if("dataset" in data["datasets"][x]):
            if(data["datasets"][x]["dataset"] == currentDataset):
                deviceIds = data["datasets"][x]["deviceIds"]

    #return deviceIds
    return deviceIds


def Get_db_names():
    """
    Collect and return database name initials from the Cloudant storage
    """
    #connect to Cloudant
    cloudantClient.connect()

    #get all database names
    dbnames = cloudantClient.all_dbs()
    dbnamesLength = len(dbnames)

    #initalize uniqueDbnames
    uniqueDbnames = []

    #loop through all database names
    for x in range(0, dbnamesLength):
        if("iotp" in dbnames[x]):
            #get the initial database name with out the date
            dbInitialNameSplit = dbnames[x].split("_")
            dbInitialName = dbInitialNameSplit[0] + "_" + dbInitialNameSplit[1] + "_" + dbInitialNameSplit[2] + "_"

            #get length of uniqueDbnames
            uniqueDbnamesLength = len(uniqueDbnames)

            #set uniqueDbnamesExists to false
            uniqueDbnamesExists = False

            #loop through uniqueDbnames, if found set uniqueDbnamesExists to true
            for j in range(0, uniqueDbnamesLength):
                if (dbInitialName == uniqueDbnames[j]):
                    uniqueDbnamesExists = True

            #if entry does not exist, then create new one
            if uniqueDbnamesExists == False:
                uniqueDbnames.append(dbInitialName)

    #disconnect from Cloudant
    cloudantClient.disconnect()

    #return uniqueDbnames
    return uniqueDbnames


def Get_db_dates():
    """
    Collect and returns dates from the Cloudant storage
    """
    #connect to Cloudant
    cloudantClient.connect()

    #get all database names
    dbnames = cloudantClient.all_dbs()
    dbnamesLength = len(dbnames)

    #initalize uniqueDbnames
    uniqueDates = []

    #loop through all database names
    for x in range(0, dbnamesLength):
        if("iotp" in dbnames[x]):
            #get the date from the database name
            dbNameSplit = dbnames[x].split("_")
            dbDate = dbNameSplit[3]

            #get length of uniqueDates
            uniqueDatesLength = len(uniqueDates)

            #set uniqueDatesExists to false
            uniqueDatesExists = False

            #loop through uniqueDates, if found set uniqueDbnamesExists to true
            for j in range(0, uniqueDatesLength):
                if (dbDate == uniqueDates[j]):
                    uniqueDatesExists = True

            #if entry does not exist, then create new one
            if (uniqueDatesExists == False) and ("-" in dbDate):
                uniqueDates.append(dbDate)

    #disconnect from Cloudant
    cloudantClient.disconnect()

    #return uniqueDates
    return uniqueDates


def Get_db_deviceids():
    """
    Collect and returns dates from the Cloudant storage
    """
    #connect to Cloudant
    cloudantClient.connect()

    #get all database names
    dbnames = cloudantClient.all_dbs()
    dbnamesLength = len(dbnames)

    #disconnect from Cloudant
    cloudantClient.disconnect()

    #initalize uniqueDeviceIds and count for loop
    uniqueDeviceIds = []
    count = 0

    #loop through all database names
    for x in range(0, dbnamesLength):
        if("iotp" in dbnames[x]) and ("-" in dbnames[x]) and count < 11:
            #assign database name
            databaseName = dbnames[x]

            #connect to Cloudant database and retrieve data for the database
            cloudantClient.connect()
            endPoint = '{0}/{1}'.format(serviceURL, databaseName + "/_all_docs")
            params = {'include_docs': 'true'}
            response = cloudantClient.r_session.get(endPoint, params=params)
            data = response.json()

            #get length of rows
            rowsLength = len(data["rows"])

            #loop through data
            for y in range(0, rowsLength):
                #get deviceId from each row
                if("deviceId" in data["rows"][y]["doc"]):
                    deviceID = data["rows"][y]["doc"]["deviceId"]

                    #get length of uniqueDeviceIds
                    uniqueDeviceIdsLength = len(uniqueDeviceIds)

                    #set uniqueDeviceIdsExists to false
                    uniqueDeviceIdsExists = False

                    #loop through uniqueDeviceIds, if found set uniqueDbnamesExists to true
                    for j in range(0, uniqueDeviceIdsLength):
                        if (deviceID == uniqueDeviceIds[j]):
                            uniqueDeviceIdsExists = True

                    #if entry for data does not exist, then create new one
                    if uniqueDeviceIdsExists == False:
                        uniqueDeviceIds.append(deviceID)

            #increment count
            count += 1

            #disconnect from Cloudant
            cloudantClient.disconnect()

    #retrun uniqueDeviceIds
    return uniqueDeviceIds


def Append_dataset(inputDeviceIds, inputDates, inputDatasetName, inputDbName):
    """
    Append dataset.json file with user inputs
    """
    output = {}

    #get deviceIds and dates as array from user inputs
    deviceIds = inputDeviceIds.split(",")
    dates = inputDates.split(",")

    #create datasetObj and assign user inputs
    datasetObj = {}
    datasetObj["databaseName"] = inputDbName
    datasetObj["dataset"] = inputDatasetName
    datasetObj["dates"] = dates
    datasetObj["deviceIds"] = deviceIds

    #read json from datasets.json file
    with open('datasets.json', 'r') as data_file:
        data = json.load(data_file)
        data_file.close()

    #append datasetObj to datasets
    data["datasets"].append(datasetObj)

    #update datasets.json file
    with open('datasets.json', 'w') as outfile:
        json.dump(data, outfile)
        outfile.close()

    #return with dataset name
    output = {"dataset": inputDatasetName}
    return output


def Get_database():
    """
    Collect and returns active dataset database initial
    """
    #read json from datasets.json file
    with open('datasets.json', 'r') as data_file:
        data = json.load(data_file)
        data_file.close()

    #get the active dataset
    currentDataset = data["currentDataset"]
    datasetsLength = len(data["datasets"])

    #loop through datasets and get the database names initial for the active dataset
    for x in range(0, datasetsLength):
        if("dataset" in data["datasets"][x]):
            if(data["datasets"][x]["dataset"] == currentDataset):
                databaseName = data["datasets"][x]["databaseName"]

    #return the database names initial
    return databaseName
