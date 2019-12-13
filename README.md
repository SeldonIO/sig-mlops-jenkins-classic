# MLOps with Seldon and Jenkins Classic

This repository shows how you can build a Jenkins Classic pipeline to enable Continuous Integration and Continuous Delivery (CI/CD) on your Machine Learning models leveraging Seldon for deployment.
This CI/CD pipeline will allow you to:

- Run unit tests using Jenkins Classic.
- Run end-to-end tests for your model with KIND (Kubernetes in Docker).
- Promote your model as a across multiple (staging / prod) environments.

To showcase these features we will implement add continuous integration and delivery to three different models. 
You can find these under the `/models` folder.
As we shall see, each of them will require a [different approach to deployment](#Use-Cases).

## CI/CD Pipeline

The diagram below provides a high level overview of the CI/CD pipeline.
It includes an overview of all the different types of repositories, together with the stakeholders that are the primary contributors of each, as well as the Kubernetes environments in which the applications are deployed.

The key pieces to note on the diagram are:

- There are different types of environments with different restrictions and behaviours, e.g. staging and production.
- It’s possible to have more than one environment for each type (as the type is just what would give it a specific type of config/behaviour).
- The environments are by default in the same cluster (as namespaces), however it’s also possible to configure them across different clusters.
- Each of the green boxes is a single repository, but it can also have a mono-repo approach, whereby each of the white boxes is a folder within a repo.

![CI/CD Pipeline](./images/pipeline-architecture.jpg)

**TODO:** Link each type to its own folder.

### Model implementation repository

From a high-level point of view, when a model implementation repository is updated by a Data Scientist or ML Engineer, the Jenkins CI will push changes to the [GitOps repository](#gitops-repository). This enables the following workflow:

1. A Data Scientist or ML Engineer trains a new model.
2. The Data Scientist or ML Engineer pushes the updated configuration to the model implementation repository.
3. The CI tool automatically builds and tests the model implementation.
4. The CI tool automatically pushes the change into the GitOps staging repository.
5. The CI tool automatically opens a PR into the GitOps production repository.

One key point to highlight which may not be obvious by just looking at the diagram is that in this phase of model implementation, the example above showcases how we can leverage a re-usable model server - that is, reusing a pre-built docker image instead of building one every time.
If there are more custom requirements, the user is in full control of the steps performed by the CI Platform Jenkins.
This means that it is also possible to build s2i wrapped components which may require training the image every time.

To gain a better understanding of how the CI/CD pipeline is implemented on each model implementation repository you can check the documented [deep dive](./docs/deep-dive.md).

#### Why a new repo for every model?

A new model implementation repo is currently created because it provides us with a way to separate the “Model Deployment” phase and the “Model Training/Experimentation” phase, and allows us to use the repo as the integration between any frameworks that can serve as sources of models (MLFlow, Kubeflow, Spark, etc).
The repo is able to store any metadata, IDs, and configuration files required, and is processed through the CI pipeline every time it is modified. 

#### Building a docker image in model implementation repository

Whilst most of the times users of this approach will be leveraging re-usable model servers such as the SKLearn model server, it is also possible to build a docker image every single time (i.e. build a non-reusable model every time a model changes).
This can be be done by adding the relevant steps which would most often include the s2i utility.
This may be desired if there are non-standard linux libraries or non-standard depdencies that need to be re-installed every time. 

### GitOps repository

**TODO:** All resources? Helm charts or just specs?

The state of each of our environments (e.g. production or staging) is stored on a GitOps repository.
This repository contains all the different Kubernetes resources that have been deployed to each cluster.
It is linked through ArgoCD to each of our Kubernetes clusters (or namespaces) so that a change in the repository triggers an update of our environment.

When the deployment configuration of a machine learning model implementation is updated, this will automatically make the changes available through a PR to the respective manager/tech-lead/approver.
This step will enable the end to end machine learning model promotion to be reviewed and approved by the respective individual.

The manager/tech-lead will have to approve the PR before it can be merged.
Once it’s approved, it will be merged into the GitOps repo, which will immediately trigger the update in the production namespace/cluster.

### Re-usable model server repository

If there is a need for a new reusable model server, then it’s possible to do so by creating a repository which would follow a different path.
This would be different to the model implementation repository as it would only be built once in a while, whilst the model server would be built multiple times.

## Set up

As a pre-requisite you need to ensure that have access to a Kubernetes cluster.
In particular, this guide requires the following pre- requisites:

- A Kubernetes cluster running v1.13+.
- Jenkins Classic installed in your cluster.
- Seldon Core v0.5.1 installed in your cluster.

**TODO:** Add note on ArgoCD (or Seldon Deploy??)

### Jenkins Config

The configurations required in the Jenkins server are:

- Install the GitHub Plugin [(for automated webhook triggers)](https://support.cloudbees.com/hc/en-us/articles/115003015691-GitHub-Webhook-Non-Multibranch-Jobs).
- Provide a GitHub token with read access so it can clone relevant repositories.
- Set-up webhooks so that GitHub can send push requests.

## Use cases

**TODO:** Add links to separate notebooks.

This guide goes through three different methods to build and deploy your model.

- Using Seldon pre-built re-usable model servers. 
- Using custom re-usable servers.
- Using custom servers with an embedded model.

## Next steps

The following resources go into more practical and deeper aspects of how MLOps can be implemented with Seldon on Jenkins Classic.

- [Deep dive](./docs/deep-dive.md). Walkthrough on the different parts of the CI/CD pipeline for a model implementation repository. 
- **TODO:** Add notebook on how to create a CI/CD pipeline
- **TODO:** Add notebook on how to set up the K8s cluster (e.g. install Jenkins, secrets, etc)


```python

```
