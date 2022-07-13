# Contents
- [Contents](#contents)
	- [Multimodal Data Visualization Microservice for Open EII](#multimodal-data-visualization-microservice-for-open-eii)
	- [Prerequisites](#prerequisites)
	- [Run the containers](#run-the-containers)
	- [Grafana](#grafana)

## Multimodal Data Visualization Microservice for Open EII

The Multimodal Data Visualization Microservice is a microservice that can visualize the video streaming and time series data. Two containers runs as a part of this microservice, multimodal-data-visualization and multimodal-data-visualization-streaming. multimodal-data-visualization-streaming container gets the ingested frames and inference results from the MsgBus subscriber and render the video to the webpage. This webpage is embedded in Grafana to visualize the video stream and other time series data on the same dashboard. This directory provides a Docker compose
and config file to use Multimodal Data Visualization Microservice with the Open Edge Insights software stack.

>**Note:** In this document, you will find labels of ‘Edge Insights for Industrial (EII)’ for filenames, paths, code snippets, and so on. Consider the references of EII as Open EII. This is due to the product name change of EII as Open EII.

## Prerequisites

As a prerequisite for Multimodal Data Visualization Microservice, complete the following steps:

1. Run the following commands to get the Open EII source code:

   ```sh
    repo init -u "https://github.com/open-edge-insights/eii-manifests.git"
    repo sync
   ```

   >**Note:** For more details, refer [here](https://github.com/open-edge-insights/eii-manifests).

2. Complete the prerequisite for provisioning the Open EII stack by referring to the
[README.md](https://github.com/open-edge-insights/eii-core/blob/master/README.md#provision).

3. Run the following commands to set the environment, build the `ia_configmgr_agent` container:

   ```sh
   cd [WORK_DIR]/IEdgeInsights/build

   # Execute the builder.py script
   python3 builder.py -f usecases/video-streaming.yml
   ```

## Run the containers

To pull the prebuilt Open EII container images and Multimodal Data Visualization Microservice images from Docker Hub and run the containers in the detached mode, run the following command:

```sh
# Start the docker containers
docker-compose up -d
```

> **Note:**
>
> The prebuilt container image for the [Multimodal Data Visualization Microservice](https://hub.docker.com/r/intel/edge_video_analytics_microservice)
> gets downloaded when you run the `docker-compose up -d` command, if the image is not already present on the host system.

### Interfaces section

In the Open EII mode, the endpoint details for the Open EII service you need to subscribe from are to be provided in the **Subscribers** section in the [config](config.json) file.
For more details on the structure, refer to the [Open EII documentation](https://github.com/open-edge-insights/eii-core/blob/master/README.md#add-oei-services).


### Grafana
Once the Microservice is up, Grafana can be accessed on http://<HOST_IP>:3000. It supports various storage backends for the time-series data (data source). Open Edge Insights (OEI) uses InfluxDB as the data source. Grafana connects to the InfluxDB data source which has been preconfigured as a part of the Grafana setup. The 'ia_influxdbconnector' and ia_webservice service must be running for Grafana to be able to collect the time-series data and stream the video respectively. After the data source starts working, you can use the preconfigured dashboard to visualize the incoming data. You can also edit the dashboard as required.
The following are the configuration details for Grafana:

- [dashboard.json](../multimodal-data-visualization/eii/dashboard.json): This is the dashboard json file that is loaded when Grafana starts. It is preconfigured to display the time-series data.

- [dashboard.yml](../multimodal-data-visualization/eii/dashboard.yml): This is the config file for all the dashboards. It specifies the path to locate all the dashboard json files.

- [datasource.yml](../multimodal-data-visualization/eii/datasource.yml): This is the config file for setting up the data source. It has various fields for data source configuration.

- [grafana.ini](../multimodal-data-visualization/eii/grafana.ini): This is the config file for Grafana. It specifies how Grafana should start after it is configured.

>**Note:** You can edit the contents of these files based on your requirement.


### Perform the following steps to run Grafana for a video use case:

1. Ensure that the endpoint of the publisher, that you want to subscribe to, is mentioned in the **Subscribers** section of the [config](config.json) file.
2. On the **Home Dashboard** page, on the left corner, click the Dashboards icon.
3. Click the **Manage Dashboards** tab, to view the list of all the preconfigured dashboards.
4. Select **EII Video and Time Series Dashboard**, to view multiple panels with topic names of the subscriber as the panel names along with a time-series panel named `Time Series`.
5. Hover over the topic name. The panel title will display multiple options.
6. Click **View** to view the subscribed frames for each topic.

>**NOTE:**
>
> 1. Changing gridPos for the video frame panels is prohibited since these values are altered internally to support multi instance.
> 2. Grafana does not support visualization for GVA, CustomUDF streams


