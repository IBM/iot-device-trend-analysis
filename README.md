# Create an IoT device trend analysis and visualization app

In this code pattern, we will create a web application to visualize IoT data to view trends and stats of devices across days. We will store the data from IoT platform in a Cloudant database using IoT Platform's built in ability to store data directly to a database on our IBM Cloud.  

The application will access the data from the Cloudant database's daily store to create analytical visualization of the data.  The plotly js plots are used to create these visualizations of the data based on user inputs.  The plotly js provides a great way to display data visually through numerous plot types and ability to manage and enhance on plots.

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
1. [IoT Platform setup](#1-iot-platform-setup)
2. [Cloudant as data store](#2-cloudant-as-data-store)
3. [Clone the repo](#3-clone-the-repo)
4. [Configure .env file](#4-configure-env-file)
5. [Run Application](#5-run-application)
6. [Deploy to IBM Cloud](#6-deploy-to-ibm-cloud)


## 1. IoT Platform setup

Create [Internet of Things Platform](https://console.bluemix.net/registration/?target=/catalog/services/internet-of-things-platform) service. Next setup devices in your IoT Platform which would transmit data.  You can follow this guide to [create devices](https://developer.ibm.com/recipes/tutorials/how-to-register-devices-in-ibm-iot-foundation/).

The app is designed to handle payload including the following fields:
```
  "deviceId": "d6a82126d",
  "timestamp": "2018-04-04T11:36:31.046Z",
  "data": {
    "connections": 58,
    "deviceCount": 78,
    "activeClients": 68
  }
```

Here the data fields are `connections`, `deviceCount` and `activeClients`, which are analyzed by the app to view trends in their values across time.

In the IBM IoT Platform, you can [simulate data](https://console.bluemix.net/docs/services/IoT/devices/device_sim.html#sim_device_data) sent through by the devices. This can be done through `Settings`, by enabling `Active Device Simulator` under `Experimental Features`.  Find `Settings` option on your left tab:

<p align="left">
  <img height="400"  src="readme_images/options-settings.png">
</p>

And next enable the `Active Device Simulator` under `Experimental Features`

<p align="center">
  <img width="500"  src="readme_images/features-simulate.png">
</p>


Once you have enabled the simulation, you can update the payload and frequency of data sent by the device.  The simulated data can look similar to below:
<p align="center">
  <img width="500"  src="readme_images/simulate_device.png">
</p>




## 2. Cloudant as data store

Next create a [Cloudant database](https://console.bluemix.net/catalog/services/cloudant-nosql-db) in IBM Cloud.

Then, configure the IBM Watson Iot Platform to set up Cloudant database as daily store.

Go to `Extensions` on you IoT Platform

<p align="left">
  <img height="400"  src="readme_images/iot-plaform-options.png">
</p>

Under `Historical Data Storage`, choose `Setup` and find your Cloudant database.  

<p align="center">
  <img width="400"  src="readme_images/historical-data-storage.png">
</p>

Set up your `Bucket Interval` for `Day` and click `Done`

<p align="center">
  <img height="200"  src="readme_images/setup-interval.png">
</p>

Now your cloudant database is set to receive data from Watson IoT Platform.  In your Cloudant, you should view a database for each day now:

<p align="center">
  <img width="700"  src="readme_images/cloudant-database.png">
</p>

You should view similar data in your Cloudant json as below:

<p align="center">
  <img width="350"  src="readme_images/cloudant-json.png">
</p>


## 3. Clone the repo

In a directory of your choice, clone the repo:
```
git clone https://github.com/IBM/iot-device-trend-analysis
```

## 4. Configure .env file

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


## 5. Run Application

Now you are ready to run your application. Go into this project's root directory
+ Run `pip install -r requirements.txt` to install the app's dependencies
+ Run `python run.py`
+ Access the running app in a browser at <http://0.0.0.0:5000/>

<p align="center">
  <img width="650"  src="readme_images/app-interface.png">
</p>

### Create dataset

Before analyzing you will need to create a dataset which includes the database inital name, dates and device Ids.  You can do through the app by going to `Create Dataset`

<p align="center">
  <img width="450"  src="readme_images/create-dataset.png">
</p>


Or you can manually edit the `datasets.json` file which should look like below:
```
{
  "currentDataset": "New1",
  "datasets": [
    {
      "databaseName": "iotp_nmghmm_default_",
      "dataset": "New1",
      "dates": [
        "2018-01-28",
        "2018-01-29",
        "2018-01-30"
      ],
      "deviceIds": [
        "830ab1575",
        "bc1a6275a",
        "1d0c388d0",
        "51bdc89e4"
      ]
    }
  ]
}
```

### Analyze the data

Once you have defined your dataset, you are ready to analyze your data through the different options present on the homepage. Each analysis will ask for device(s) and date(s) to generate the plot. Once your plot is generated, you can explore different plotly interactive options on the top right which can allow to download the plot, change the plot type and other actions.

<p align="center">
  <img width="650"  src="readme_images/hourly-stats.png">
</p>

## 6. Deploy to IBM Cloud

Edit the `manifest.yml` file in the folder that contains your code and replace with a unique name for your application. The name that you specify determines the application's URL, such as `your-application-name.mybluemix.net`. Additionally - update the service names so they match what you have in IBM Cloud. The relevant portion of the `manifest.yml` file looks like the following:


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

In the command line use cloud foundry command to push the application to IBM Cloud:
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
