# EnterpriseAI-Project
** WIP **

Essential steps

  - [ ] Find and download (static) data set of your choice
  - [ ] Split it into training, validation and test set. Put the test set aside. The test should later be used to "simulate" prediction requests during production.
  - [ ] Perform feature engineering
  - [ ] Train a ML Model of your choice
  - [ ] Evaluate the model using at least one benchmark (see lecture 6)
  - [ ] Put the model in production on a server
  - [ ] Create an app where users can query predictions from the model
  - [ ] Use the data from your test set to send prediction requests to your model
  - [ ] Track all your experiments and code versions in your team (and describe how you did this in your project documentation)

  

Ideas for additional steps (ordered from less to more difficult)

  - [ ] Establish procedures for data validation (and document them!)
  - [ ] Test feature importance to identify the most relevant features for your model (see lecture 4)
  - [ ] Improve your machine learning model, e.g. by performing hyperparameter tuning or by creating an ensemble (see lecture 6)
  - [ ] Include a feature in your app for users to give feedback on the quality of the predictions
  - [ ] In case you have little data and/or few labels, apply some data augmentation techniques and/or programmatic labeling techniques (see lecture 4)
  - [ ] Evaluate the fairness and robustness of your model with some of the techniques mentioned in the lecture. For example, conduct a slice-based evaluation, perform perturbation tests (e.g. to simulate an adversarial attack)
  - [ ] Optimize your model, to reduce inference latency and/or model size
  - [ ] Simulate varying traffic levels of prediciton requests. Make your deployment scalable to adapt to the se varying levels
  - [ ] Simulate a model update in production (e.g. via a shadow deployment, A/B test, a canary release,…)
  - [ ] Get access to a data source that is updated over time. Use it instead of using the static dataset mentioned above. Establish the appropiate measures to handle drift by validating the incoming data. Monitor the performance of your model.
  - [ ] In the previous setting: Establish a procedure to update your model. 
  - [ ] Create a system composed of several ML-based microservices that interact (see modes of data flow in lecture 3)

