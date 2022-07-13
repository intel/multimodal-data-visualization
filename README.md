## Multimodal Data Visualization Microservice

This repository contains the source code for Multimodal Data Visualization Microservice used for the [Video Analytics Use Case](https://www.intel.com/content/www/us/en/developer/articles/technical/video-analytics-service.html).

### Build the base image

Complete the following steps to build the base image:

1. Run the following command:

   ```sh
     docker-compose -f  docker-compose-build.yml  build
   ```

### Run the base image

Complete the following steps to run the base image:

1. Clone this [repo](https://github.com/intel-innersource/applications.services.esh.visualization-microservice).
2. Configure Host IP 'export HOST_IP=<HOST-IP-address>'
3. Run the `docker-compose up` command.

### Perform the following steps to run Grafana in EVAM mode:
1. Go to [http://<IP-Address>:3000](http://localhost:3000) to access Grafana.
2. On the **Home Dashboard** page, on the left corner, click the Dashboards icon.
3. Click the **Manage Dashboards** tab, to view the list of all the preconfigured dashboards.
4. Select **Video Analytics Dashboard**, to view the data from the Edge Video Analytics Microservice.

### Run Multimodal Data Visualization Microservice in Open EII mode

To run Multimodal Data Visualization Microservice in the Open EII mode, refer to the [README_OEI](README_OEI.md).

