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

# Diving into our CI/CD Pipeline

On this section we will dive into the internals of the CI/CD pipeline for our [model implementation repositories](#model-implementation-repository).
This includes a detailed description of the `Jenkinsfile`, as well as a look into our suggested testing methodology.

Note that this will cover a generic example.
However, as we shall see, specialising this approach into any of our [three main use cases](#use-cases) will be straightforward.

## Jenkins Pipelines

We leverage [Jenkins Pipelines](https://jenkins.io/doc/book/pipeline/) in order to run our continous integration and delivery automation.
From a high-level point of view, the pipeline configuration will be responsible for:

- Define a **replicable** test and build environment.
- Run the unit and integration tests (if applicable).
- Promote the application into our staging and production environments.
  As discussed [previously](#ci-cd-pipeline), the change will be promoted automatically to the staging environment and will require an approval in the production environment.
  
We can see a `Jenkinsfile` below taken from the [`news_classifier`](./models/news_classifier) example.
This `Jenkinsfile` defines a pipeline which takes into account all of the points mentioned above.
The following sections will dive into each of the sections in a much higher detail.

### Replicable test and build environment

In order to ensure that our test environments are versioned and replicable, we make use of the [Jenkins Kubernetes plugin](https://github.com/jenkinsci/kubernetes-plugin).
This will allow us to create a Docker image with all the necessary tools for testing and building our models.
Using this image, we will then spin up a separate pod, where all our build instructions will be ran.

Since it leverages Kubernetes underneath, this also ensure that our CI/CD pipelines are easily scalable.


```python
%%writefile jenkins-x.yml
buildPack: none
pipelineConfig:
  pipelines:
    release:
      pipeline:
        agent:
          image: seldonio/core-builder:0.4
        stages:
          - name: test-sklearn-server
            steps:
            - name: run-tests
              command: make
              args:
              - install_dev
              - test
    pullRequest:
      pipeline:
        agent:
          image: seldonio/core-builder:0.4
        stages:
          - name: test-sklearn-server
            steps:
            - name: run-tests
              command: make
              args:
              - install_dev
              - test
```

    Overwriting jenkins-x.yml


The `jenkins-x.yml` file is pretty easy to understand if we read through the different steps.

Basically we can define the steps of what happens upon `release` - i.e. when a PR / Commit is added to master - and what happens upon `pullRequest` - whenever someone opens a pull request.

You can see that the steps are exactly the same for both release and PR for now - namely, we run `make install_dev test` which basically installs all the dependencies and runs all the tests.



### Integration and unit tests

Now that we have a model that we want to be able to deploy, we want to make sure that we run end-to-end tests on that model to make sure everything works as expected.
For this we will leverage the same framework that the Kubernetes team uses to test Kubernetes itself: [KIND](https://kind.sigs.k8s.io/).

KIND stands for Kubernetes-in-Docker, and is used to isolate a Kubernetes environent for end-to-end tests.
In our case, we will use this isolated environment to test our model.

The steps we'll have to carry out include:

1. Enable Docker within your CI/CD pod.
2. Add an integration test stage.
3. Leverage the `kind_test_all.sh` script that creates a KIND cluster and runs the tests.


### Add docker auth to your cluster

Adding a docker authentication with Jenkins X can be done through a JX CLI command, which is the following:

* `jx create docker auth --host https://index.docker.io/v1/ --user $YOUR_DOCKER_USERNAME --secret $YOUR_DOCKER_KEY_SECRET --email $YOUR_DOCKER_EMAIL`

This comamnd will use these credentials to authenticate with Docker and create an auth token (which expires).

#### Extend JenkinsX file for integration

Now that we have the test that would run for the integration tests, we need to extend the JX pipeline to run this.

This extension is quite simple, and only requires adding the following line:
    
```
            - name: run-end-to-end-tests
              command: bash
              args:
              - integration/kind_test_all.sh
```

This line would be added in both the PR and release pipelines so that we can run integration tests then.

#### Enable Docker

To test our models, we will need to build their respective containers, for which we will need Docker.

In order to do so, we will first need to mount a few volumes into the CI/CD container.
These basically consist of the core components that docker will need to be able to run.
To mount them we will leverage the `volumes` argument of the `podTemplate()` method:

```groovy
podTemplate(...,
    volumes: [
      hostPathVolume(mountPath: '/sys/fs/cgroup', hostPath: '/sys/fs/cgroup'),
      hostPathVolume(mountPath: '/lib/modules', hostPath: '/lib/modules'),
      emptyDirVolume(mountPath: '/var/lib/docker'),
    ])
```

We then need to make sure that the pod can run with privileged context.
This step is required in order to be able to run the `docker` daemon.
To enable privileged permissions we will leverage the `privileged` flag of the `containerTemplate()` method and the `yaml` parameter of `podTemplate()`:


```groovy
podTemplate(...,
    containers: [
      containerTemplate(
          ...,
          privileged: true,
          ...
      ),
      ...],
    yaml:'''
    spec:
      securityContext:
        fsGroup: 1000
      ...
    ''',
....)
```

#### Run tests in Kind 

The `kind_run_all.sh` may seem complicated at first, but it's actually quite simple. 
All the script does is set-up a kind cluster with all dependencies, deploy the model and clean everything up.
Let's break down each of the components within the script.

We first start the docker daemon and wait until Docker is running (using `docker ps q` for guidance.

```bash
# FIRST WE START THE DOCKER DAEMON
service docker start
# the service can be started but the docker socket not ready, wait for ready
WAIT_N=0
while true; do
    # docker ps -q should only work if the daemon is ready
    docker ps -q > /dev/null 2>&1 && break
    if [[ ${WAIT_N} -lt 5 ]]; then
        WAIT_N=$((WAIT_N+1))
        echo "[SETUP] Waiting for Docker to be ready, sleeping for ${WAIT_N} seconds ..."
        sleep ${WAIT_N}
    else
        echo "[SETUP] Reached maximum attempts, not waiting any longer ..."
        break
    fi
done
```



Once we're running a docker daemon, we can run the command to create our KIND cluster, and install all the components.
This will set up a Kubernetes cluster using the docker daemon (using containers as Nodes), and then install Ambassador + Seldon Core.


```bash
#######################################
# AVOID EXIT ON ERROR FOR FOLLOWING CMDS
set +o errexit

# START CLUSTER 
make kind_create_cluster
KIND_EXIT_VALUE=$?

# Ensure we reach the kubeconfig path
export KUBECONFIG=$(kind get kubeconfig-path)

# ONLY RUN THE FOLLOWING IF SUCCESS
if [[ ${KIND_EXIT_VALUE} -eq 0 ]]; then
    # KIND CLUSTER SETUP
    make kind_setup
    SETUP_EXIT_VALUE=$?
```

We can now run the tests; for this we run all the dev installations and kick off our tests (which we'll add inside of the integration folder).

```bash
    # BUILD S2I BASE IMAGES
    make build
    S2I_EXIT_VALUE=$?

    ## INSTALL ALL REQUIRED DEPENDENCIES
    make install_integration_dev
    INSTALL_EXIT_VALUE=$?
    
    ## RUNNING TESTS AND CAPTURING ERROR
    make test
    TEST_EXIT_VALUE=$?
fi
```


Finally we just clean everything, including the cluster, the containers and the docker daemon.

```bash
# DELETE KIND CLUSTER
make kind_delete_cluster
DELETE_EXIT_VALUE=$?

#######################################
# EXIT STOPS COMMANDS FROM HERE ONWARDS
set -o errexit

# CLEANING DOCKER
docker ps -aq | xargs -r docker rm -f || true
service docker stop || true
```

### Promote your application
Now that we've verified that our CI pipeline is working, we want to promote our application to production

This can be done with our JX CLI:


```python
!jx promote application --...
```

#### Test your production application

Once your production application is deployed, you can test it using the same script, but in the `jx-production` namespace:


```python
from seldon_core.seldon_client import SeldonClient
import numpy as np

url = !kubectl get svc ambassador -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

sc = SeldonClient(
    gateway="ambassador", 
    gateway_endpoint="localhost:80",
    deployment_name="mlops-server",
    payload_type="ndarray",
    namespace="jx-production",
    transport="rest")

response = sc.predict(data=np.array([twenty_test.data[0]]))

response.response.data
```
