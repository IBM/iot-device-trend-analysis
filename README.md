# Create an IoT device trend analysis and visualization app

In this code pattern, we will create a web application to visualize IoT data to view trends and stats of devices across days. We will store the data from IoT platform in a cloudant database.  The application will access the data from the cloudant database's daily store to create analytical visualization of the data.  The plotly js plots are used to create visualizations based on user inputs.  The plotly js provides a great way to display data visually through numerous plot types and ability to manage and enhance on plots.

# Architecture Flow

<p align="center">
  <img width="600"  src="readme_images/arch_flow.png">
</p>


1. The Iot data is stored in Cloudant database as daily buckets
2. The data from Cloudant is used to create plotly visualizatons
3. The plot is displayed through the Web UI based on user requests
4. The user can view the plots and perform analysis on each plot through the web UI


## Included Components

+ [IBM Watson IoT Platform](https://console.bluemix.net/registration/?target=/catalog/services/internet-of-things-platform)
+ [Cloudant](https://www.ibm.com/analytics/us/en/technology/cloud-data-services/cloudant/)
+ [Plotly js](https://plot.ly/javascript/)


## Steps
1. [IoT Platform Data Store](#1-IoT-Platform-Data-Store)
2. [Clone the repo](#2-clone-the-repo)
3. [Configure .env file](#3-configure-env-file)
4. [Run Application](#4-run-application)
5. [Deploy to IBM Cloud](#5-configure-manifest-file-and-deploy-to-ibm-cloud)



## 1. IoT Platform Data Store

Create [Internet of Things Platform service](https://console.bluemix.net/registration/?target=/catalog/services/internet-of-things-platform)

Follow these guides to [create devices](https://developer.ibm.com/recipes/tutorials/how-to-register-devices-in-ibm-iot-foundation/) and [simulate data](https://console.bluemix.net/docs/services/IoT/devices/device_sim.html#sim_device_data)

The app is designed to handle payload including the following fields:
```
"deviceID": "19ca0a0b6",
"timeStamp": "2018-01-16T10:35:41.635Z",
"activeClients": 65.0,
"deviceCount": 85.0,
"connections": 43.0
```


Next create a [Cloudant database](https://console.bluemix.net/catalog/services/cloudant-nosql-db) in IBM Cloud.

Configure the IBM Watson Iot Platform to set up Cloudant database as daily store.

Go to `Extensions` on you IoT Platform

<p align="left">
  <img height="400"  src="readme_images/iot-plaform-options.png">
</p>

Under `Historical Data Storage`, choose `Setup` and find your Cloudant database.  

<p align="center">
  <img width="200"  src="readme_images/historical-data-storage.png">
</p>

Set up your `Bucket Interval` for `Day` and click `Done`

<p align="center">
  <img height="200"  src="readme_images/setup-interval.png">
</p>

Now your cloudant database is set to receive data from Watson IoT Platform.

## 2. Clone the repo

In a directory of your choice, clone the repo:
```
git clone
```

## 3. Configure .env file

Create a `.env` file in the root directory of your clone of the project repository by copying the sample `.env.example` file using the following command:

  ```none
  cp .env.example .env
  ```

You will need to update the credentials for the Cloudant database which you created.

The `.env` file will look something like the following:

  ```none
  #Cloudant NoSQL database
  CLOUDANT_USERNAME=
  CLOUDANT_PASSWORD=
  CLOUDANT_URL=
  ```


## 4. Update iot database name, devices and dates

In `run.py` update database name, dates and deviceIds to create the dataset you would like to plot.

```none
iotDatabaseName = "iotp_nmghmm_default_"

#hard coded deviceIds
deviceIds = ['19ca0a0b6','02e356e3a','2eeae108d','c270d3f23','19c94a94f',
                '38a42a88e','076814d5e','7c45d2861','a0c91d0f8','f788dc541']

#hard coded dates
dates = ['2018-01-16','2018-01-17','2018-01-18','2018-01-19','2018-01-20',
            '2018-01-21','2018-01-22','2018-01-23','2018-01-24','2018-01-25']
```


## 5. Run Application

cd into this project's root directory
+ Run `pip install -r requirements.txt` to install the app's dependencies
+ Run `python run.py`
+ Access the running app in a browser at <http://0.0.0.0:5000/>



## 6. Deploy to IBM Cloud

Edit the `manifest.yml` file in the folder that contains your code and replace with a unique name for your application. The name that you specify determines the application's URL, such as `your-application-name.mybluemix.net`. Additionally - update the service names so they match what you have in Bluemix. The relevant portion of the `manifest.yml` file looks like the following:


```
applications:
- path: .
  memory: 512M
  instances: 1
  domain: mybluemix.net
  name: Iot-Analytics
  host: slam-iot-analytics
  disk_quota: 1024M
  buildpack: python_buildpack
  services:
  - cloudant
```

In the command line use the following command to push the application to IBM Cloud:
```
cf push
```


## Troubleshooting
To troubleshoot your IBM Cloud application, use the logs. To see the logs, run:

```bash
cf logs <application-name> --recent
```

# License

[Apache 2.0](LICENSE)
