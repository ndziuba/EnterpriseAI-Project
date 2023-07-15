# EnterpriseAI-Project
With this project we set up a mlops pipeline to predict the potential of a wildfire on specific, user-given coordinats. 

The project is based on [this](https://www.kaggle.com/datasets/abdelghaniaaba/wildfire-prediction-dataset) kaggle dataset. In this dataset, the creator added satellite images of coordinates in canada, where there previously has been a wildfire or currently is a wildfire, based on another wildfire api. Mapbox doesn't allow the specification of when the pictures are taken and thats why we can't tell, if there is a wildfire currently ongoing in the image or not.

We trained a customized ResNet50 model on the dataset and added our own data with the same procedure as in the original dataset, to allow an active flow of new data to the model and set up a [web-app](https://eai.dziubalabs.de/) for users to run the prediction.

The input images of the models are images like shown below and the output is a classification to either wildfire potential or not with a corresponding confidence.


![-61 5607,50 52878](https://github.com/ndziuba/EnterpriseAI-Project/assets/83732214/c640c65b-2132-4ddb-a5ec-f9804c40cbd0)

<p align="center">
  <img width="350" height="350" src="[-61 5607,50 52878](https://github.com/ndziuba/EnterpriseAI-Project/assets/83732214/c640c65b-2132-4ddb-a5ec-f9804c40cbd0)">
</p>

## Folder structure:

    container/:  Includes all files to spin up the base infrastructure.
    data/:       All files regarding the data used in model training 
    k8s/:        All files regarding the production and staging deployment.
    k8s/config:  All files to configure the secrets, certificates and the ingress for yatai.
    models/:     All generated models while executing pipeline
    pipelines/:  Contains the pipelines used in the project
    steps/:      All steps that are used in the mlops pipeline
    webapp:      The Next.js React App as frontend for the model.


## Practical project walkthrough
TBD


## Infrastructur
This section provides an overview of the infrastructure of the project, all .example files are for demonstration and have to be stripped of the .example for production.

### Serverstructur
The project utilizes one server hosting different Docker containers and a Kubernetes Cluster, where the nodes are running on Digital Ocean. The server also provides CLI Access to the Cluster where Kubernetes can be configured.

    Caddy: The reverse proxy for the server, the config can be found in containers/caddy/proxy/Caddyfile

#### Docker Server
In the folder container, a <code>container/docker-compose.yml.example</code> is provided setting the base infrastructure up for the project. After a <code>docker-compose up -d</code> the server provides the following services:

    Caddy:       The reverse proxy for the server, the config can be found in containers/caddy/proxy/Caddyfile
    Zenml:       A Zenml 0.41 Server gets provided saving its data in a SQlite Database.
    Minio:       A S3 compatible service as object storage for Zenml and MLflow, also saving the DVC data.
    Prometheus:  To monitor the server Prometheus, including cadvisor and node-exporter, are set up.
    Grafana:     To show dashboards of the gathered data from Prometheus.

A <code>.env.example</code> is provided that has to be configured for production.

#### Kubernetes
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


### Continuous Integration and Deployment
Yatai is the cloud deployment infrastructure for BentoML and represents our CI/CD pipeline. 
This project is used to manage Bentofiles in a repository, build the Docker Images and deploy them to Kubernetes.
While most of the steps are automated by default, the process after pushing a Bentofile to Yatai had to be automated with a script.
After the push Yatai does not build Images, it only builds them when a Bentofile gets put into a deployment.
But it also has no functionality of automatically putting a Bentofile into deployment after a push.

To fix these issues and enable Continuous Delivery, the <code>update_deployment.sh</code> script utilizing <code>get_bento_version.py</code>
extract the latest pushed Bentofile and deploy it into the staging deployment.
Yatai then builds the Image and after this process finishes successfully the current staging model gets changed with a rolling release.
This can either be run manually or in our case automated with a Cronjob.

WIP

## ZenML pipeline

### data_loader step
The data_loader step is a part of the training pipeline. It fetches wildfire data from the Canada Wildfire Service(https://cwfis.cfs.nrcan.gc.ca/downloads/activefires/activefires.csv), filters it based on a specified timeframe (daydelta parameter), and retrieves satellite images of the wildfires from the Mapbox API. This step mimics the origin of the Kaggle dataset and creates additional training, valid and test data, enabling a continuous change in the model. 

The step returns the count of images saved, which is useful for understanding the volume of data added in each run.

### hp_tuner step
The hp_tuner step tunes the hyperparameters of the model, specifically the number of neuron in the hidden layer we added on top of the original ResNet50 model. First it loads the necessary data and concatenates the additional data we added to the original dataset with the train and validation datasets. After that the Keras tuner starts to build the model. Our model consists of the basic resnet50 model (all the weights of the layers of the pretrained model will be excluded from training), an additional Flatten layer, are Dense layer of variable size and a relu activation function (Rectifier Linear Unit) and at last an output layer for the two classes with a softmax activation function. After building the model, the tuner starts the hp search with the specified amount of epochs for the sizes 128, 256 and 512 of the hidden layer. After the completion of the search, the step returns the optimal model for the current data.

### trainer step
The trainer step further trains the optimal model returned in the hp_tuning step. At the beginning the necessary data for the step is loaded and again concatenatet with our own additional data. The trainer then fits the model for the additional specified amount of epochs

### evaluator step
The evaluator step loads the new model and the current production model and returns the model accuracy on the test dataset respectively.

### bento_builder step
The bento_builder step starts the building of the bento with the new model. It specifies, which data in the repository to exclude from building and which python packages to include in the final bento. Furthermore the corresponding service.py spcifies how the runner should work in production. We configured the bento to get an image as the input and return an array with the confidence of the corresponding class and the model version used to run the prediction.

### discord_alter step
A simple alerting mechanism builds in the pipeline to notify us via our discord of updates. It follows the structure of (https://github.com/zenml-io/zenml-projects/blob/main/nba-pipeline/steps/discord_bot.py). The step takes the deployment decision and the test_evaluation accuracy and uses the discord webhook interface to send the message.

### trigger_decision step
Step comparing the accuracy of the newly trained model and the model currently in deployment and returns a bool.

### deployer step 
Pushes the last build bento to Yatai, from where it gets deployed into our staging model. It further saves the model to compare its performance in the next iteration. 

## Notebooks

### enrich_data
This notebook used MapBox and geoAPI to enrich the training data with no wildfire pictures from cities with similar geographical makeup as Canada. For each entry in a list of 128 Cities, the geo API is used to gather its coordinates. A random noise of ~ 5 km^2 is added for each coordinate, and the MapBox API is called to generate an image. This gets repeated 50 times per city to add 6400 additional samples to our data. We assume that the images depict cities and their surroundings. We can safely classify them as no wildfire.  

### model_experiments
This notebook was used to do the initial experiments for deciding which basic model architecture to use in our project. As you can see in the notebook, we found corrupt images in our source dataset and removed them. In regard to the model architecture, we tested different batch sizes, different layers and layer sizes, we experimented with retraining all the resnet layer weights and different base models such as different ResNet and DenseNet sizes. The results can be seen inside the notebook. Finally we did our first predictions using the mapbox api.

### hp_tuning_test
This notebook was used to test hyperparameter tuning on our model. As described in the hp_tuner step, we used the keras tuner package. We experimented with different layer sizes and activation functions with five epochs each. The results can be seen inside the notebook.

## Major challanges

### Tensorflow GPU
Not specifically relevant to the project as we could have used cloud infrastructure for training, but getting tensorflow with gpu support to run correctly on a windows machine was a major struggle.

### Service integration
With using many services as zenml, mlflow, yatai, bento etc. we often got into dependency hell but after some tinkering it worked eventually. But either way a sometimes frustrating experience.

### Infrastructure problems
Pushing our bentos to yatai posed a challange aswell, because multiple problems like filesize limits and database errors like bento-tag limits to 128 VARCHARs needed some attention to work the way we imagined


WIP



# ~~The following Section needs to be deleted before finishing the project~~

Documentation:
TODO:
  - UseCase
  - Daten (Ursprung, kaggle usw.)
  - continous deployment

Mendel: Model(trainer, hp_tuner, evaluator, bento builder

Tim: Data loader, discord, trigger decision, deployer

Nicholas: Infrastruktur, dvc, dagshub, zenml, mlflow, yatai, webapp

Essential steps

  - [X] Find and download (static) data set of your choice
  - [X] Split it into training, validation and test set. Put the test set aside. The test should later be used to "simulate" prediction requests during production.
  - [ ] ~~Perform feature engineering~~
  - [X] Train a ML Model of your choice
  - [X] Evaluate the model using at least one benchmark (see lecture 6)
  - [x] Put the model in production on a server
  - [x] Create an app where users can query predictions from the model
  - [ ] Use the data from your test set to send prediction requests to your model
  - [X] Track all your experiments and code versions in your team (and describe how you did this in your project documentation)

  

Ideas for additional steps (ordered from less to more difficult)

  - [X] Establish procedures for data validation (and document them!)
  - [ ] ~~Test feature importance to identify the most relevant features for your model (see lecture 4)~~
  - [X] Improve your machine learning model, e.g. by performing hyperparameter tuning or by creating an ensemble (see lecture 6)
  - [ ] Include a feature in your app for users to give feedback on the quality of the predictions
  - [X] In case you have little data and/or few labels, apply some data augmentation techniques and/or programmatic labeling techniques (see lecture 4)
  - [ ] ~~Evaluate the fairness and robustness of your model with some of the techniques mentioned in the lecture. For example, conduct a slice-based evaluation, perform perturbation tests (e.g. to simulate an adversarial attack)~~
  - [ ] (WIP m3ndel, evtl. model compression)Optimize your model, to reduce inference latency and/or model size
  - [ ] (Wird manuell möglich sein) Simulate varying traffic levels of prediciton requests. Make your deployment scalable to adapt to the varying levels
  - [x] Simulate a model update in production (e.g. via a shadow deployment, A/B test, a canary release,…)
  - [X] Get access to a data source that is updated over time. Use it instead of using the static dataset mentioned above. Establish the appropiate measures to handle drift by validating the incoming data. Monitor the performance of your model.
  - [x] In the previous setting: Establish a procedure to update your model. 
  - [X] Create a system composed of several ML-based microservices that interact (see modes of data flow in lecture 3)

