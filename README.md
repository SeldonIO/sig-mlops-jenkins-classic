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

**TODO:** Include graphic here and explain pipeline

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

# Diving into our continuous integration

**TODO:** Make this section general (applicable to the diff models)!

**TODO:** Use Jenkins Classic instead of Jenkins X

We have now separated our model development into two chunks: 

* The first one involves the creation of a model serve, and the second one involves the CI of the model server, and the second involves the deployment of models that create the model.


## Using the Jenkins X pipeline

In order to do this we will be able to first run some tests and the push to the docker repo.

For this we will be leveraging the Jenkins X file, we'll first start with a simple file that just runs the tests:


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

# Integration tests

Now that we have a model that we want to be able to deploy, we want to make sure that we run end-to-end tests on that model to make sure everything works as expected.

For this we will leverage the same framework that the Kubernetes team uses to test Kubernetes itself: KIND.

KIND stands for Kubernetes in Docker, and is used to isolate a Kubernetes environent for end-to-end tests.

In our case, we will be able to leverage to create an isolated environment, where we'll be able to test our model.

For this, the steps we'll have to carry out include:

1. Authenticate your docker with the jx CLI
2. Add the steps in the `Jenkins-X.yml` to run this in the production cluster
3. Leverage the `kind_run_all.sh` script that creates a KIND cluster and runs the tests


## Add docker auth to your cluster

Adding a docker authentication with Jenkins X can be done through a JX CLI command, which is the following:

* `jx create docker auth --host https://index.docker.io/v1/ --user $YOUR_DOCKER_USERNAME --secret $YOUR_DOCKER_KEY_SECRET --email $YOUR_DOCKER_EMAIL`

This comamnd will use these credentials to authenticate with Docker and create an auth token (which expires).

## Extend JenkinsX file for integration

Now that we have the test that would run for the integration tests, we need to extend the JX pipeline to run this.

This extension is quite simple, and only requires adding the following line:
    
```
            - name: run-end-to-end-tests
              command: bash
              args:
              - integration/kind_test_all.sh
```

This line would be added in both the PR and release pipelines so that we can run integration tests then.

It is also possible to move the integration tests into a separate jenkins-x file such as `jenkins-x-integration.yml` by leveraging [Contexts & Schedules]() which basically allow us to extend the functionality of Prow by writing our own triggers, however this is outside the scope of this tutorial.

### Config to provide docker authentication

This piece is slightly more extensive, as we will need to use Docker to build out containers due to the dependency on `s2i` to build the model wrappers.

First we need to define the volumes that we'll be mounting to the container.

The first few volumes before basically consist of the core components that docker will need to be able to run.
```
          volumes:
            - name: modules
              hostPath:
                path: /lib/modules
                type: Directory
            - name: cgroup
              hostPath:
                path: /sys/fs/cgroup
                type: Directory
            - name: dind-storage
              emptyDir: {}
```
We also want to mount the docker credentials which we will generate in the next step.
```
            - name: jenkins-docker-config-volume
              secret:
                items:
                - key: config.json
                  path: config.json
                secretName: jenkins-docker-cfg
```
Once we've created the volumes, now we just need to mount them. This can be done as follows:
```
        options:
          containerOptions:
            volumeMounts:
              - mountPath: /lib/modules
                name: modules
                readOnly: true
              - mountPath: /sys/fs/cgroup
                name: cgroup
              - name: dind-storage
                mountPath: /var/lib/docker                 
```
And finally we also mount the docker auth configuration so we don't have to run `docker login`:
```
              - mountPath: /builder/home/.docker
                name: jenkins-docker-config-volume
```

And to finalise, we need to make sure that the pod can run with privileged context.

The reason why this is required is in order to be able to run the docker daemon:
```
            securityContext:
              privileged: true
```

## Kind run all integration tests script

The kind_run_all may seem complicated at first, but it's actually quite simple. 

All the script does is set-up a kind cluster with all dependencies, deploy the model and clean everything up.

Let's break down each of the components within the script.

#### Start docker

We first start the docker daemon and wait until Docker is running (using `docker ps q` for guidance.

```
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

#### Create and set-up KIND cluster

Once we're running a docker daemon, we can run the command to create our KIND cluster, and install all the components.

This will set up a Kubnernetes cluster using the docker daemon (using containers as Nodes), and then install Ambassador + Seldon Core.

```
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

#### Run python tests

We can now run the tests; for this we run all the dev installations and kick off our tests (which we'll add inside of the integration folder).

```
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

#### Clean up

Finally we just clean everything, including the cluster, the containers and the docker daemon.

```
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


# Promote your application
Now that we've verified that our CI pipeline is working, we want to promote our application to production

This can be done with our JX CLI:


```python
!jx promote application --...
```

## Test your production application

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


```python

```
