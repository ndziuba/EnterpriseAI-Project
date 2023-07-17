# Enterprise AI Project - Wildfire prediction<img width="50" height="50" src="https://github.com/ndziuba/EnterpriseAI-Project/assets/83732214/f7cdcca1-74a6-4cdf-9bbc-b0eaa533849a">


With this project, we set up an MLOps pipeline to predict the potential of a wildfire on specific, user-given coordinates. 

The project is based on [this](https://www.kaggle.com/datasets/abdelghaniaaba/wildfire-prediction-dataset) Kaggle dataset. In the dataset, the creator added satellite images of coordinates in Canada, where there previously has been a wildfire or currently is a wildfire, based on another wildfire API. Mapbox doesn't allow the specification of when the pictures are taken and that's why we can't tell, if there is a wildfire currently ongoing in the image or not.

We trained a customized ResNet50 model on the dataset and added our own data with the same procedure as in the original dataset, to allow an active flow of new data to the model and set up a [web-app](https://eai.dziubalabs.de/) for users to run the prediction.

The input images of the models are images like shown below and the output is a classification of either wildfire potential or not with corresponding confidence.

<p align="center">
  <img width="350" height="350" src="https://github.com/ndziuba/EnterpriseAI-Project/assets/83732214/c640c65b-2132-4ddb-a5ec-f9804c40cbd0">
</p>

## Workflow

Our Workflow Stack consists of the following illustrated technologies and services.
<p align="center">
  <img width="800" height="100%" src="https://github.com/ndziuba/EnterpriseAI-Project/assets/26720962/d103d20a-62c2-4a51-889d-cd51ec325377">
</p>

## Folder structure

    container/:  Includes all files to spin up the base infrastructure with Docker.
    data/:       All files regarding the data used in model training.
    k8s/:        All files regarding the production and staging deployment in Kubernetes.
    k8s/config:  All files to configure the secrets, certificates and the ingress for Yatai.
    models/:     All generated models while executing pipeline.
    pipelines/:  Contains the pipelines used in the project.
    steps/:      All steps that are used in the mlops pipeline.
    webapp:      The Next.js React App as frontend for the model.

## Practical project walkthrough

Start the pipeline execution

    python run.py

After that, the following tasks will be executed (a detailed explanation of the individual steps and pipeline can be found in the following sections):

    - zenml starts pipeline execution
      - pipeline/training_pipeline will be called with parameter: epochs=5, path='data', batch_size=32, hp_tuning_epochs=1
        - steps/data_loader will be called 
        - steps/hp_tuner will be called with set parameters
        - steps/trainer will be called with the tuner-optimal model; mlflow starts logging training
        - steps/bento_builder starts building a bento file based on the trained model
        - steps/evaluator evaluates the performance of newly trained and production model
        - steps/trigger_decision compares accuracy and decides if the new model is better
        - steps/deployer deploys model to yatai based on the trigger decision
        - steps/discord_bot posts alert that a new model has been pushed 
    - Yatai automatically updates pods to new version and builds containers
        
## Infrastructure
This section provides an overview of the infrastructure of the project, all .example files are for demonstration and have to be stripped of the .example for production.
The project utilizes one VPS server hosted on Netcup hosting different Docker containers and a Kubernetes Cluster where the nodes are running on Digital Ocean. The Netcup VPS also provides CLI Access to the Cluster where Kubernetes can be configured.

### Docker Server
In the folder container, a <code>container/docker-compose.yml.example</code> is provided setting the base infrastructure up for the project. After a <code>docker-compose up -d</code> the server provides the following services:

    Caddy:       The reverse proxy for the server, the config can be found in containers/caddy/proxy/Caddyfile
    Zenml:       A Zenml 0.41 Server gets provided saving its data in a SQlite Database.
    Mlflow:      A Mlflow Server that gets build from a Dockerfile and secured by HTTP Basic Auth.
    Minio:       A S3 compatible service as object storage for Zenml and MLflow, also saving the DVC data.
    Prometheus:  To monitor the server Prometheus, including cadvisor and node-exporter, are set up.
    Grafana:     To show dashboards of the gathered data from Prometheus.

A <code>.env.example</code> is provided that has to be configured for production.

### Kubernetes
The Kubernetes Cluster is a four-node Cluster hosting our production deployment with Yatai.
Being in the early development of a restructure the documentation for Yatai is either lacking or functionalities are changed, not working as documented or some basic functionality is missing.
For example, the Bento Deployments from Yatai can't be configured with a tls secret for the nginx-ingress to add a certificate to the endpoint.
This can be omitted by deploying the Bentos from the CLI, adding a tls secret in the YAML, as shown in the <code>k8s/prod-deployment.yml.example</code> and <code>k8s/staging-deployment.yml.example</code>.
These YAML files provide a production and staging deployment in Kubernetes, where the staging is our challenging model, with their respective endpoints. 
To have a single endpoint with a A/B test the <code>k8s/predict-ingress.yml.example</code> sets up a separate nginx-ingress splitting the traffic with a canary rule for predict.yatai.<DOMAIN> 50/50 between the two deployments.
This also configuration also provides the ability by terminating the staging environment to again route all traffic to the production deployment.
To secure all endpoints with a certificate the configuration examples for Cert Manager are provided under <code>k8s/config</code>.

The Cluster provides the following services:

    Yatai:            Yatai is manually set up by the instruction on their website because the automatic installer is not 
                      working in Azure and Digital Ocean. 
                      This deployment includes yatai, yatai-image-builder and yatai-deployment.
    Docker registry:  A local Docker registry is provided for yatai-image-builder to commit the build images to.
    Nginx Ingress:    Our ingress controller which manages all incoming traffic.
    Cert Manager:     A service providing ACME Let's Encrypt certificates for the endpoints, 
                      using the <code>k8s/config/externaldns.yml</code> to update the Digital Ocean DNS.
    Prometheus:       To get metrics for the deployments and the cluster with metrics-server.
    Grafana:          To provide the dashboards for the Kubernetes environment.

### Dagshub
Because Github has a file size limit we had to use S3 as Storage for our DVC. But because Github can not integrate with S3 Buckets we additionally used Dagshub, a data science oriented git repository.
With Dagshub we can integrate S3 Buckets directly into the Repository and use them to store our DVC data.
Dagshub also provides a hosted DVC, but we use our self-hosted Minio S3 to store the files and just added it to the Repository.
Additionally, Dagshub provides a hosted Mlflow, but because we self-hosted a newer version we also did not use it.
Despite that, if we did not self-host the infrastructure we would have used more of this service.

## Continuous Integration and Deployment with Yatai
Yatai is the cloud deployment infrastructure for BentoML and represents our CI/CD pipeline. 
This project is used to manage Bentofiles in a repository, build the Docker Images and deploy them to Kubernetes.
While most of the steps are automated by default, the process after pushing a Bentofile to Yatai had to be automated with a script.
After the push Yatai does not build Images, it only builds them when a Bentofile gets put into a deployment.
But it also has no functionality of automatically putting a Bentofile into deployment after a push.

To fix these issues and enable Continuous Delivery, the <code>update_deployment.sh</code> script utilizing <code>get_bento_version.py</code>
extracts the latest pushed Bentofile and deploys it into the staging deployment.
Yatai then builds the Image and after this process finishes successfully it does a rolling release, exchanging the current staging model.
This can either be run manually or in our case automated with a Cronjob.
After a successful A/B Test, the production environment gets manually set to the new Bento.

To use the scripts the server has to have python3, jq, pip, bentoml, and minio installed.
Also, the user has to login into Yatai, as further shown, with the server that is running the scripts.

      apt install python3 jq pip
      pip install minio bentoml python-dotenv pathlib
      bentoml yatai login --api-token {YOUR_TOKEN_GOES_HERE} --endpoint http://yatai.$DOMAIN

To automatically run the pipeline in predefined intervals, we added the option to run the pipeline on a fixed schedule for a set amount of times in the run.py file. 
This option allows us to continuously update the model with up-to-date data, and retrain and update the production model without any additional user input.

## Monitoring and Scaling Deployment

We monitor the deployment requests with Grafana and Prometheus as shown in the following picture, it shows our 50/50 traffic split and resource usage.
The information is extracted through endpoints in our Pods provided by BentoML that feed their metrics into Prometheus, where then a Dashboard in Grafana is set up to visualize them.

![grafik](https://github.com/ndziuba/EnterpriseAI-Project/assets/26720962/d2b459e1-9bfe-4879-a8b2-85c35211a60d)

Because of our Usage of Kubernetes, if the load in and decreases the deployment can scale the number of Pods accordingly based on our configuration of min and max Replications of the API Server and Runner Pods.
This scaling is also shown in the Yatai Dashboard, as shown in the following figure where with a load test of querying 1 Image per second the Runner scaled up from min 1 Pod to the max value of 2 Pods.

![grafik](https://github.com/ndziuba/EnterpriseAI-Project/assets/26720962/1095a42a-11e8-4e9a-9daa-4e0321e56300)



## Next.js React App

As frontend for our Model, we use a React App built on the Next.js framework. It utilizes Leaflet to show an OpenStreetMap to pick the Latitude and Longitude on click.
These coordinates get sent to the serverside Backend to get processed to query the Mapbox API. 
Mapbox then returns the queried image and the App then queries our Predict endpoint, which responds with the confidence and Bento tag to the Backend.

The App outputs this information together with the queried image to the User and the possibility to give feedback for the prediction.
This feedback containing an id, the image as Base64, coordinates, prediction, feedback, and model version gets saved in an SQLite Database inside the Next.js Application.


 ![grafik](https://github.com/ndziuba/EnterpriseAI-Project/assets/26720962/6859689f-d14c-4f4c-9dac-45bf462f52dc)


To run the app on a server a Dockerfile was configured to build a container, with for example <code>docker build</code>.
To then deploy it either <code>docker run</code> or the provided <code>docker-compose.yml</code> with <code>docker-compose up -d</code> can be used.




## ZenML pipeline

### data_loader step
The data_loader step is a part of the training pipeline. It fetches wildfire data from the [Canada Wildfire Service](https://cwfis.cfs.nrcan.gc.ca/downloads/activefires/activefires.csv), filters it based on a specified timeframe (day delta parameter), and retrieves satellite images of the wildfires from the Mapbox API. This step mimics the origin of the Kaggle dataset and creates additional training, valid and test data, enabling a continuous change in the model. 

The step returns the count of images saved, which is useful for understanding the volume of data added in each run.

### hp_tuner step
The hp_tuner step tunes the hyperparameters of the model, specifically the number of neurons in the hidden layer we added on top of the original ResNet50 model. First, it loads the necessary data and concatenates the additional data we added to the original dataset with the train and validation datasets. After that, the Keras tuner starts to build the model. Our model consists of the basic resnet50 model (all the weights of the layers of the pre-trained model will be excluded from training), an additional Flatten layer, are Dense layer of variable size, and a ReLU activation function (Rectifier Linear Unit), and at last an output layer for the two classes with a softmax activation function. After building the model, the tuner starts the hp search with the specified amount of epochs for the sizes 128, 256, and 512 of the hidden layer. After the completion of the search, the step returns the optimal model for the current data.

### trainer step
The trainer step further trains the optimal model returned in the hp_tuning step. In the beginning, the necessary data for the step is loaded and again concatenated with our own additional data. The trainer then fits the model for the additional specified amount of epochs

### evaluator step
The evaluator step loads the new model and the current production model and returns the model accuracy on the test dataset respectively.

### bento_builder step
The bento_builder step starts the building of the bento with the new model. It specifies, which data in the repository to exclude from building and which Python packages to include in the final bento. Furthermore, the corresponding service.py specifies how the runner should work in production. We configured the bento to get an image as the input and return an array with the confidence of the corresponding class and the model version used to run the prediction.

### discord_alert step
A simple alerting mechanism builds in the pipeline to notify us via our discord of updates. It follows the structure of [this](https://github.com/zenml-io/zenml-projects/blob/main/nba-pipeline/steps/discord_bot.py) repo. The step takes the deployment decision and the test_evaluation accuracy and uses the discord webhook interface to send the message.

### trigger_decision step
Step comparing the accuracy of the newly trained model and the model currently in deployment and returns a bool.

### deployer step 
Pushes the last build bento to Yatai, from where it gets deployed into our staging model. It further saves the model to compare its performance in the next iteration. 

## Notebooks

### enrich_data
This notebook used MapBox and geoAPI to enrich the training data with no wildfire pictures from cities with similar geographical makeup as Canada. For each entry in a list of 128 Cities, the geo API is used to gather its coordinates. A random noise of ~ 5 km^2 is added for each coordinate, and the MapBox API is called to generate an image. This gets repeated 50 times per city to add 6400 additional samples to our data. We assume that the images depict cities and their surroundings. We can safely classify them as no wildfire.  

### model_experiments
This notebook was used to do the initial experiments for deciding which basic model architecture to use in our project. As you can see in the notebook, we found corrupt images in our source dataset and removed them. In regard to the model architecture, we tested different batch sizes, different layers, and layer sizes, we experimented with retraining all the ResNet layer weights and different base models such as different ResNet and DenseNet sizes. The results can be seen inside the notebook. Finally, we did our first predictions using the Mapbox API.

### integrated_gradient_test
To better understand the workings of our model we applied the explainable AI method of Integrated Gradients (IG). We followed this [tutorial](https://www.tensorflow.org/tutorials/interpretability/integrated_gradients). 
The technique generates interpolations between a baseline (a black image) and the image. Generating the relevant gradients for each interpolation. A mask can be created with these gradients, highlighting the relevant pixels for the prediction.

### hp_tuning_test
This notebook was used to test hyperparameter tuning on our model. As described in the hp_tuner step, we used the Keras tuner package. We experimented with different layer sizes and activation functions with five epochs each. The results can be seen inside the notebook.

### model_compression
This notebook was used to test and explore the options to compress the model size, as our current model (mainly the ResNet base model) is comparably large. We tried implementing a pruning step to cut down the inference time and size of the model but it didn't lead to any significant performance gains.
The only method that brought down the size of the model from 95mb to around 20mb was converting our model to a TFlite model but given the proprietary model architecture this change would have resulted in a lot of work adapting the pipeline and we did not consider it worth it in our case.

### api_load_test
This notebook was used to get a feeling of how our API server handles load balancing and how it performs on longer sustained loads. As data, we randomly sampled 1/6th of our test dataset (overall accuracy 0.91) and scored a 0.74 accuracy on the sampled test data, but accuracy was not the focus in this experiment, as we already know how our model performs on the test dataset. The average inference time was 2.63 seconds per image request.

## Major challenges

### Tensorflow GPU
Not specifically relevant to the project as we could have used cloud infrastructure for training, but getting TensorFlow with GPU support to run correctly on a Windows machine was a major struggle.

### Service integration
With using many services such as ZenML, MLflow, Yatai, BentoML, etc. we often got into dependency hell but after some tinkering, it worked eventually. But either way a sometimes frustrating experience.

### Infrastructure problems
Pushing our bentos to Yatai posed a challenge as well because multiple problems like file size limits and database errors like bento-tag limits to 128 VARCHARs needed some changes in the Database to work with the <code>bentoml push</code> command.
As a fix, the Postgres Database for Yatai had to be altered for being able to push Bentofiles to:

    \d yatai
    ALTER TABLE "label" ALTER COLUMN "value" TYPE varchar(256);  
    ALTER TABLE "model_repository" ALTER COLUMN "name" type varchar(256);

Also because Yatai does not provide a way to get the latest Bentofile that was pushed and the way mentioned in [this GitHub Issue](https://github.com/bentoml/BentoML/issues/2551) does not work anymore,
the python script <code>get_bento_version.py</code> was created to extract this information as a workaround from the Minio S3 Bucket.

Using the Yatai Web Dashboard is also limited as many changes have to be done in the CLI. As earlier described adding a tls secret can only be done in the YAML configuration, but also setting resource limits in the Dashboard is limited to only be used
if no changes in the CLI are made. Because otherwise these changes will be overridden as even if these values are not set in the YAML, the current one will then be overridden by an empty value, so values have to be set resulting in overriding the current values.
And because our Deployment automation uses the CLI in the <code>update_deployment.sh</code> script, because Yatai does not provide this functionality, the changes for staging have to be done in the <code>staging-deployment.yml</code>.

Because of the use of TensorFlow and an Image model, which need a lot of memory, the Image Builder was constantly running into memory limits. Despite having four nodes with 8 Gb of Memory, 6 GB of that usable, each.
But the Pod that gets created does not specify enough memory allocation and there is no setting to change that yet. So when the Pod gets scheduled onto a wrong node it fails.
As these Image Builder Pods are failing, they can not be restarted from the Dashboard, they have to be killed through Kubernetes, then they are redeployed and start the build process again.
Nodes with more memory would help but we were not able to get them from Digital Ocean without upgrading our Account.


