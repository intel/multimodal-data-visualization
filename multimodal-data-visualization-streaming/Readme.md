## Multimodal Data Visualization Streaming

Multimodal Data Visualization Streaming is part of Multimodal Data Visualization microservice which helps in streaming the processed video to the Webpage. This URL where the streaming is happening is used in Grafana based Visualization service for Visualization.
For e.g., in EVAM mode, it uses WebRTC framework to get the processed video from Edge Video Analytics service and stream it to the Web Page. This Web page is embedded in Grafana Dashboard using the AJAX panel to visualize the stream along with the other metrics related to Video Processing.
Similarly, in EII mode, the Webservice gets the ingested frames and inference results from the MsgBus subscriber and render the video to the webpage. This webpage is then used in Grafana for Visualization.
