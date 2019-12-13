# Diving into our CI/CD Pipeline

On this section we will dive into the internals of the CI/CD pipeline for our [model implementation repositories](#model-implementation-repository).
This includes a detailed description of the `Jenkinsfile`, as well as a look into our suggested testing methodology.

Note that this will cover a generic example.
However, as we shall see, specialising this approach into any of our [three main use cases](#use-cases) will be straightforward.

We leverage [Jenkins Pipelines](https://jenkins.io/doc/book/pipeline/) in order to run our continous integration and delivery automation.
From a high-level point of view, the pipeline configuration will be responsible for:

- Define a **replicable** test and build environment.
- Run the unit and integration tests (if applicable).
- Promote the application into our staging and production environments.
  
We can see a `Jenkinsfile` below taken from the [`news_classifier`](./models/news_classifier) example.
This `Jenkinsfile` defines a pipeline which takes into account all of the points mentioned above.
The following sections will dive into each of the sections in a much higher detail.


```python
!pygmentize -l groovy ./models/news_classifier/Jenkinsfile
```

    [37m//properties([pipelineTriggers([githubPush()])])[39;49;00m
    
    [36mdef[39;49;00m label = [33m"worker-${UUID.randomUUID().toString()}"[39;49;00m
    
    podTemplate(label: label, 
      workspaceVolume: dynamicPVC(requestsSize: [33m"4Gi"[39;49;00m),
      containers: [
      containerTemplate(
          name: [33m'news-classifier-builder'[39;49;00m, 
          image: [33m'seldonio/core-builder:0.4'[39;49;00m, 
          command: [33m'cat'[39;49;00m, 
          ttyEnabled: [34mtrue[39;49;00m,
          privileged: [34mtrue[39;49;00m,
          resourceRequestCpu: [33m'200m'[39;49;00m,
          resourceLimitCpu: [33m'500m'[39;49;00m,
          resourceRequestMemory: [33m'1500Mi'[39;49;00m,
          resourceLimitMemory: [33m'1500Mi'[39;49;00m,
      ),
      containerTemplate(
          name: [33m'jnlp'[39;49;00m, 
          image: [33m'jenkins/jnlp-slave:3.35-5-alpine'[39;49;00m, 
          args: [33m'${computer.jnlpmac} ${computer.name}'[39;49;00m)
    ],
    yaml:[33m'''[39;49;00m
    [33mspec:[39;49;00m
    [33m  securityContext:[39;49;00m
    [33m    fsGroup: 1000[39;49;00m
    [33m  containers:[39;49;00m
    [33m  - name: jnlp[39;49;00m
    [33m    imagePullPolicy: IfNotPresent[39;49;00m
    [33m    resources:[39;49;00m
    [33m      limits:[39;49;00m
    [33m        ephemeral-storage: "500Mi"[39;49;00m
    [33m      requests:[39;49;00m
    [33m        ephemeral-storage: "500Mi"[39;49;00m
    [33m  - name: news-classifier-builder[39;49;00m
    [33m    imagePullPolicy: IfNotPresent[39;49;00m
    [33m    resources:[39;49;00m
    [33m      limits:[39;49;00m
    [33m        ephemeral-storage: "15Gi"[39;49;00m
    [33m      requests:[39;49;00m
    [33m        ephemeral-storage: "15Gi"[39;49;00m
    [33m'''[39;49;00m,
    volumes: [
      hostPathVolume(mountPath: [33m'/sys/fs/cgroup'[39;49;00m, hostPath: [33m'/sys/fs/cgroup'[39;49;00m),
      hostPathVolume(mountPath: [33m'/lib/modules'[39;49;00m, hostPath: [33m'/lib/modules'[39;49;00m),
      emptyDirVolume(mountPath: [33m'/var/lib/docker'[39;49;00m),
    ]) {
      node(label) {
        [36mdef[39;49;00m myRepo = checkout scm
        [36mdef[39;49;00m gitCommit = myRepo.[36mGIT_COMMIT[39;49;00m
        [36mdef[39;49;00m gitBranch = myRepo.[36mGIT_BRANCH[39;49;00m
        [36mdef[39;49;00m shortGitCommit = [33m"${gitCommit[0..10]}"[39;49;00m
        [36mdef[39;49;00m previousGitCommit = sh(script: [33m"git rev-parse ${gitCommit}~"[39;49;00m, returnStdout: [34mtrue[39;49;00m)
     
        stage([33m'Test'[39;49;00m) {
          container([33m'news-classifier-builder'[39;49;00m) {
            sh [33m"""[39;49;00m
    [33m          pwd[39;49;00m
    [33m          make -C models/news_classifier \[39;49;00m
    [33m            install_dev \[39;49;00m
    [33m            test [39;49;00m
    [33m          """[39;49;00m
          }
        }
    
        [37m/* stage('Test integration') { */[39;49;00m
          [37m/* container('news-classifier-builder') { */[39;49;00m
            [37m/* sh 'models/news_classifier/integration/kind_test_all.sh' */[39;49;00m
          [37m/* } */[39;49;00m
        [37m/* } */[39;49;00m
    
        stage([33m'Promote application'[39;49;00m) {
          container([33m'news-classifier-builder'[39;49;00m) {
            withCredentials([[$class: [33m'UsernamePasswordMultiBinding'[39;49;00m,
                  credentialsId: [33m'github-access'[39;49;00m,
                  usernameVariable: [33m'GIT_USERNAME'[39;49;00m,
                  passwordVariable: [33m'GIT_PASSWORD'[39;49;00m]]) {
    
              sh [33m'models/news_classifier/promote_application.sh'[39;49;00m
            }
          }
        }
      }
    }


## Replicable test and build environment

In order to ensure that our test environments are versioned and replicable, we make use of the [Jenkins Kubernetes plugin](https://github.com/jenkinsci/kubernetes-plugin).
This will allow us to create a Docker image with all the necessary tools for testing and building our models.
Using this image, we will then spin up a separate pod, where all our build instructions will be ran.

Since it leverages Kubernetes underneath, this also ensure that our CI/CD pipelines are easily scalable.

**TODO:** Add note on `podTemplate()` object.

## Integration tests

Now that we have a model that we want to be able to deploy, we want to make sure that we run end-to-end tests on that model to make sure everything works as expected.
For this we will leverage the same framework that the Kubernetes team uses to test Kubernetes itself: [KIND](https://kind.sigs.k8s.io/).

KIND stands for Kubernetes-in-Docker, and is used to isolate a Kubernetes environent for end-to-end tests.
In our case, we will use this isolated environment to test our model.

The steps we'll have to carry out include:

1. Enable Docker within your CI/CD pod.
2. Add an integration test stage.
3. Leverage the `kind_test_all.sh` script that creates a KIND cluster and runs the tests.


### Add integration stage to Jenkins

We can leverage Jenkins Pipelines to manage the different stages of our CI/CD pipeline.
In particular, to add an integration stage, we can use the `stage()` object:

```groovy
stage('Test integration') {
  container('news-classifier-builder') {
    sh 'models/news_classifier/integration/kind_test_all.sh'
  }
}
```

### Enable Docker

To test our models, we will need to build their respective containers, for which we will need Docker.

In order to do so, we will first need to mount a few volumes into the CI/CD container.
These basically consist of the core components that docker will need to be able to run.
To mount them we will leverage the `volumes` argument of the `podTemplate()` object:

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
To enable privileged permissions we will leverage the `privileged` flag of the `containerTemplate()` object and the `yaml` parameter of `podTemplate()`:


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

### Run tests in Kind 

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

## Promote your application
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
