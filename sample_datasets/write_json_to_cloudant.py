import os
import json

from cloudant.client import Cloudant

from datetime import timedelta, date
import time

#cloudant credentials
serviceUsername = ""
servicePassword = ""
serviceURL = ""

#data folder
data_folder = "January"

#initialize dates
start_date = date(2018, 1, 15)
end_date = date(2018, 1, 26)

#initalize database name initial
database_name_initial =  "iotp_nmghmm_default_"

#connect to cloudant
cloudantClient = Cloudant(serviceUsername, servicePassword, url=serviceURL)
cloudantClient.connect()

#return date range
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

#loop through the json files for each day and add to the cloudant instance as a database
for single_date in daterange(start_date, end_date):

    #create the database name with the initial and date
    print (single_date.strftime("%Y-%m-%d"))
    database_date = single_date.strftime("%Y-%m-%d")
    databaseName = database_name_initial + database_date
    print (databaseName)

    #create database
    newDatabase = cloudantClient.create_database(databaseName)

    #read the json file
    json_file = databaseName + '.json'

    # get the current script path.
    here = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(here, data_folder, json_file)

    with open(filepath, 'r') as infile:
        data_array = json.load(infile)
        infile.close()

    for data_element in data_array:
        #create document in the database
        newDocument = newDatabase.create_document(data_element)
