# Image Classifier

Implementation of an image classifier model, based in [PyTorch's MNIST example](https://github.com/pytorch/examples/blob/master/mnist/main.py).

## Training

First we will train a machine learning model, which will help us classify news across multiple categories.
This model will use a custom reusable server, responsible for loading a PyTorch model.

### Install dependencies 

We will need the following dependencies in order to run the Python code:


```python
!pygmentize src/requirements.txt
```

    torch==1.3.1
    torchvision==0.4.2


We can now install the dependencies using the make command:


```python
!make install_dev
```

    cat: VERSION: No such file or directory
    Makefile:10: warning: overriding recipe for target 'make'
    Makefile:7: warning: ignoring old recipe for target 'make'
    Makefile:14: warning: overriding recipe for target 'make'
    Makefile:10: warning: ignoring old recipe for target 'make'
    pip install -r src/requirements.txt
    Requirement already satisfied: torch==1.3.1 in /home/agm/.pyenv/versions/3.6.9/lib/python3.6/site-packages (from -r src/requirements.txt (line 1)) (1.3.1)
    Requirement already satisfied: torchvision==0.4.2 in /home/agm/.pyenv/versions/3.6.9/lib/python3.6/site-packages (from -r src/requirements.txt (line 2)) (0.4.2)
    Requirement already satisfied: numpy in /home/agm/.pyenv/versions/3.6.9/lib/python3.6/site-packages (from torch==1.3.1->-r src/requirements.txt (line 1)) (1.17.4)
    Requirement already satisfied: pillow>=4.1.1 in /home/agm/.pyenv/versions/3.6.9/lib/python3.6/site-packages (from torchvision==0.4.2->-r src/requirements.txt (line 2)) (6.2.1)
    Requirement already satisfied: six in /home/agm/.pyenv/versions/3.6.9/lib/python3.6/site-packages (from torchvision==0.4.2->-r src/requirements.txt (line 2)) (1.12.0)
    [33mWARNING: You are using pip version 19.2.3, however version 19.3.1 is available.
    You should consider upgrading via the 'pip install --upgrade pip' command.[0m


### Download the ML data

Now that we have all the dependencies we can proceed to download the data.

We will download the news stories dataset, and we'll be attempting to classify across the four classes below.


```python
from src.data import fetch_training, fetch_test

training_dataset = fetch_training()
test_dataset = fetch_test()
```

We can have a look into the data to see a few examples:


```python
import matplotlib.pyplot as plt 

x_example, y_example = training_dataset[0]
plt.imshow(x_example.squeeze())
```




    <matplotlib.image.AxesImage at 0x7f1d7a519940>




![png](README_files/README_9_1.png)


### Train a model

Now that we've downloaded the data, we can train the ML model using a simple pipeline with basic text pre-processors and a Multiclass naive bayes classifier


```python
import torch
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR

from src.data import fetch_test, fetch_training
from src.train import train_epoch, test_epoch
from src.model import Classifier

batch_size = 256
epochs = 2
lr = 1.0
gamma = 0.7

train_loader = torch.utils.data.DataLoader(
    training_dataset, batch_size=batch_size, shuffle=True
)
test_loader = torch.utils.data.DataLoader(
    test_dataset, batch_size=batch_size, shuffle=True
)

model = Classifier()
optimizer = optim.Adadelta(model.parameters(), lr=lr)

scheduler = StepLR(optimizer, step_size=1, gamma=gamma)
for epoch in range(1, epochs + 1):
    train_epoch(model, train_loader, optimizer, epoch)
    test_epoch(model, test_loader)
    scheduler.step()
```

    Train Epoch: 1 [0/60000 (0%)]	Loss: 2.314072
    Train Epoch: 1 [2560/60000 (4%)]	Loss: 1.937630
    Train Epoch: 1 [5120/60000 (9%)]	Loss: 0.461113
    Train Epoch: 1 [7680/60000 (13%)]	Loss: 0.303022
    Train Epoch: 1 [10240/60000 (17%)]	Loss: 0.384866
    Train Epoch: 1 [12800/60000 (21%)]	Loss: 0.315486
    Train Epoch: 1 [15360/60000 (26%)]	Loss: 0.242260
    Train Epoch: 1 [17920/60000 (30%)]	Loss: 0.274990
    Train Epoch: 1 [20480/60000 (34%)]	Loss: 0.193279
    Train Epoch: 1 [23040/60000 (38%)]	Loss: 0.168615
    Train Epoch: 1 [25600/60000 (43%)]	Loss: 0.174742
    Train Epoch: 1 [28160/60000 (47%)]	Loss: 0.344227
    Train Epoch: 1 [30720/60000 (51%)]	Loss: 0.236581
    Train Epoch: 1 [33280/60000 (55%)]	Loss: 0.150894
    Train Epoch: 1 [35840/60000 (60%)]	Loss: 0.163011
    Train Epoch: 1 [38400/60000 (64%)]	Loss: 0.145040
    Train Epoch: 1 [40960/60000 (68%)]	Loss: 0.173859
    Train Epoch: 1 [43520/60000 (72%)]	Loss: 0.135148
    Train Epoch: 1 [46080/60000 (77%)]	Loss: 0.095240
    Train Epoch: 1 [48640/60000 (81%)]	Loss: 0.175763
    Train Epoch: 1 [51200/60000 (85%)]	Loss: 0.129632
    Train Epoch: 1 [53760/60000 (89%)]	Loss: 0.115358
    Train Epoch: 1 [56320/60000 (94%)]	Loss: 0.128080
    Train Epoch: 1 [58880/60000 (98%)]	Loss: 0.129241
    
    Test set: Average loss: 0.0695, Accuracy: 9763/10000 (98%)
    
    Train Epoch: 2 [0/60000 (0%)]	Loss: 0.150772
    Train Epoch: 2 [2560/60000 (4%)]	Loss: 0.095167
    Train Epoch: 2 [5120/60000 (9%)]	Loss: 0.115704
    Train Epoch: 2 [7680/60000 (13%)]	Loss: 0.120062
    Train Epoch: 2 [10240/60000 (17%)]	Loss: 0.074608
    Train Epoch: 2 [12800/60000 (21%)]	Loss: 0.084472
    Train Epoch: 2 [15360/60000 (26%)]	Loss: 0.131837
    Train Epoch: 2 [17920/60000 (30%)]	Loss: 0.031366
    Train Epoch: 2 [20480/60000 (34%)]	Loss: 0.027841
    Train Epoch: 2 [23040/60000 (38%)]	Loss: 0.065945
    Train Epoch: 2 [25600/60000 (43%)]	Loss: 0.040186
    Train Epoch: 2 [28160/60000 (47%)]	Loss: 0.104263
    Train Epoch: 2 [30720/60000 (51%)]	Loss: 0.112271
    Train Epoch: 2 [33280/60000 (55%)]	Loss: 0.124679
    Train Epoch: 2 [35840/60000 (60%)]	Loss: 0.165172
    Train Epoch: 2 [38400/60000 (64%)]	Loss: 0.053470
    Train Epoch: 2 [40960/60000 (68%)]	Loss: 0.053918
    Train Epoch: 2 [43520/60000 (72%)]	Loss: 0.104043
    Train Epoch: 2 [46080/60000 (77%)]	Loss: 0.078170
    Train Epoch: 2 [48640/60000 (81%)]	Loss: 0.056356
    Train Epoch: 2 [51200/60000 (85%)]	Loss: 0.103222
    Train Epoch: 2 [53760/60000 (89%)]	Loss: 0.081285
    Train Epoch: 2 [56320/60000 (94%)]	Loss: 0.120430
    Train Epoch: 2 [58880/60000 (98%)]	Loss: 0.130934
    
    Test set: Average loss: 0.0570, Accuracy: 9825/10000 (98%)
    


### Test single prediction

Now that we've trained our model we can use it to predict from un-seen data.

We can see below that the model is able to predict the first datapoint in the dataset correctly.


```python
y_pred = model(x_example.unsqueeze(0))
print(f"PREDICTED: {y_pred.argmax()}")
print(f"ACTUAL: {y_example}")
```

    PREDICTED: 5
    ACTUAL: 5


### Print accuracy

We can print the accuracy of the model by running the test data and counting the number of correct classes.


```python
test_epoch(model, test_loader)
```

    
    Test set: Average loss: 0.0570, Accuracy: 9825/10000 (98%)
    


## Deployment

Now we want to be able to deploy the model we just trained. This will just be as simple as updated the model binary.

### Save the trained model

First we have to save the trained model in the `src/` folder, which our wrapper will load


```python
import os

model_path = os.path.join("models", "model.pt")
torch.save(model.state_dict(), model_path)
```


    ---------------------------------------------------------------------------

    FileNotFoundError                         Traceback (most recent call last)

    <ipython-input-46-7c8efb7d3ee4> in <module>
          2 
          3 model_path = os.path.join("models", "model.pt")
    ----> 4 torch.save(model.state_dict(), model_path)
    

    ~/.virtualenvs/sig-mlops/lib/python3.6/site-packages/torch/serialization.py in save(obj, f, pickle_module, pickle_protocol)
        258         >>> torch.save(x, buffer)
        259     """
    --> 260     return _with_file_like(f, "wb", lambda f: _save(obj, f, pickle_module, pickle_protocol))
        261 
        262 


    ~/.virtualenvs/sig-mlops/lib/python3.6/site-packages/torch/serialization.py in _with_file_like(f, mode, body)
        181             (sys.version_info[0] == 3 and isinstance(f, pathlib.Path)):
        182         new_fd = True
    --> 183         f = open(f, mode)
        184     try:
        185         return body(f)


    FileNotFoundError: [Errno 2] No such file or directory: 'models/model.pt'


### Update your unit test

We'll write a very simple unit test that make sure that the model loads and runs as expected.


```python
!pygmentize src/test_model.py
```

    [34mimport[39;49;00m [04m[36mnumpy[39;49;00m [34mas[39;49;00m [04m[36mnp[39;49;00m
    [34mfrom[39;49;00m [04m[36munittest[39;49;00m [34mimport[39;49;00m mock
    [34mimport[39;49;00m [04m[36mjoblib[39;49;00m
    [34mimport[39;49;00m [04m[36mos[39;49;00m
    
    EXPECTED_RESPONSE = np.array([[34m3[39;49;00m, [34m3[39;49;00m])
    
    [34mdef[39;49;00m [32mtest_model[39;49;00m(*args, **kwargs):
        data = [[33m"[39;49;00m[33mtext 1[39;49;00m[33m"[39;49;00m, [33m"[39;49;00m[33mtext 2[39;49;00m[33m"[39;49;00m]
    
        m = joblib.load([33m"[39;49;00m[33mmodel.joblib[39;49;00m[33m"[39;49;00m)
        result = m.predict(data)
        [34massert[39;49;00m [36mall[39;49;00m(result == EXPECTED_RESPONSE)



```python
!make test
```

    cat: VERSION: No such file or directory
    Makefile:10: warning: overriding recipe for target 'make'
    Makefile:7: warning: ignoring old recipe for target 'make'
    Makefile:14: warning: overriding recipe for target 'make'
    Makefile:10: warning: ignoring old recipe for target 'make'
    (cd src && \
    	pytest -s --verbose -W ignore --log-level=INFO 2>&1)
    [1m============================= test session starts ==============================[0m
    platform linux -- Python 3.6.9, pytest-5.1.1, py-1.8.0, pluggy-0.13.1 -- /home/agm/.pyenv/versions/3.6.9/bin/python3.6
    cachedir: .pytest_cache
    rootdir: /home/agm/Seldon/sig-mlops-jenkins-classic/models/news_classifier/src
    collected 1 item                                                               [0m
    
    test_model.py::test_model [32mPASSED[0m
    
    [32m[1m============================== 1 passed in 1.05s ===============================[0m


### Updating Integration Tests

We can also now update the integration tests. This is another very simple step, where we'll want to test this model specifically.



```python
!pygmentize integration/test_e2e_seldon_model_server.py
```

    [34mfrom[39;49;00m [04m[36mseldon_core.seldon_client[39;49;00m [34mimport[39;49;00m SeldonClient
    [34mfrom[39;49;00m [04m[36mseldon_core.utils[39;49;00m [34mimport[39;49;00m seldon_message_to_json
    [34mimport[39;49;00m [04m[36mnumpy[39;49;00m [34mas[39;49;00m [04m[36mnp[39;49;00m
    [34mfrom[39;49;00m [04m[36msubprocess[39;49;00m [34mimport[39;49;00m run
    [34mimport[39;49;00m [04m[36mtime[39;49;00m
    [34mimport[39;49;00m [04m[36mlogging[39;49;00m
    
    
    API_AMBASSADOR = [33m"[39;49;00m[33mlocalhost:8003[39;49;00m[33m"[39;49;00m
    
    [34mdef[39;49;00m [32mtest_sklearn_server[39;49;00m():
        data = [[33m"[39;49;00m[33mFrom: brian@ucsd.edu (Brian Kantor)[39;49;00m[33m\n[39;49;00m[33mSubject: Re: HELP for Kidney Stones ..............[39;49;00m[33m\n[39;49;00m[33mOrganization: The Avant-Garde of the Now, Ltd.[39;49;00m[33m\n[39;49;00m[33mLines: 12[39;49;00m[33m\n[39;49;00m[33mNNTP-Posting-Host: ucsd.edu[39;49;00m[33m\n[39;49;00m[33m\n[39;49;00m[33mAs I recall from my bout with kidney stones, there isn[39;49;00m[33m'[39;49;00m[33mt any[39;49;00m[33m\n[39;49;00m[33mmedication that can do anything about them except relieve the pain.[39;49;00m[33m\n[39;49;00m[33m\n[39;49;00m[33mEither they pass, or they have to be broken up with sound, or they have[39;49;00m[33m\n[39;49;00m[33mto be extracted surgically.[39;49;00m[33m\n[39;49;00m[33m\n[39;49;00m[33mWhen I was in, the X-ray tech happened to mention that she[39;49;00m[33m'[39;49;00m[33md had kidney[39;49;00m[33m\n[39;49;00m[33mstones and children, and the childbirth hurt less.[39;49;00m[33m\n[39;49;00m[33m\n[39;49;00m[33mDemerol worked, although I nearly got arrested on my way home when I barfed[39;49;00m[33m\n[39;49;00m[33mall over the police car parked just outside the ER.[39;49;00m[33m\n[39;49;00m[33m\t[39;49;00m[33m- Brian[39;49;00m[33m\n[39;49;00m[33m"[39;49;00m,
                [33m'[39;49;00m[33mFrom: rind@enterprise.bih.harvard.edu (David Rind)[39;49;00m[33m\n[39;49;00m[33mSubject: Re: Candida(yeast) Bloom, Fact or Fiction[39;49;00m[33m\n[39;49;00m[33mOrganization: Beth Israel Hospital, Harvard Medical School, Boston Mass., USA[39;49;00m[33m\n[39;49;00m[33mLines: 37[39;49;00m[33m\n[39;49;00m[33mNNTP-Posting-Host: enterprise.bih.harvard.edu[39;49;00m[33m\n[39;49;00m[33m\n[39;49;00m[33mIn article <1993Apr26.103242.1@vms.ocom.okstate.edu>[39;49;00m[33m\n[39;49;00m[33m banschbach@vms.ocom.okstate.edu writes:[39;49;00m[33m\n[39;49;00m[33m>are in a different class.  The big question seems to be is it reasonable to [39;49;00m[33m\n[39;49;00m[33m>use them in patients with GI distress or sinus problems that *could* be due [39;49;00m[33m\n[39;49;00m[33m>to candida blooms following the use of broad-spectrum antibiotics?[39;49;00m[33m\n[39;49;00m[33m\n[39;49;00m[33mI guess I[39;49;00m[33m\'[39;49;00m[33mm still not clear on what the term [39;49;00m[33m"[39;49;00m[33mcandida bloom[39;49;00m[33m"[39;49;00m[33m means,[39;49;00m[33m\n[39;49;00m[33mbut certainly it is well known that thrush (superficial candidal[39;49;00m[33m\n[39;49;00m[33minfections on mucous membranes) can occur after antibiotic use.[39;49;00m[33m\n[39;49;00m[33mThis has nothing to do with systemic yeast syndrome, the [39;49;00m[33m"[39;49;00m[33mquack[39;49;00m[33m"[39;49;00m[33m\n[39;49;00m[33mdiagnosis that has been being discussed.[39;49;00m[33m\n[39;49;00m[33m\n[39;49;00m[33m\n[39;49;00m[33m>found in the sinus mucus membranes than is candida.  Women have been known [39;49;00m[33m\n[39;49;00m[33m>for a very long time to suffer from candida blooms in the vagina and a [39;49;00m[33m\n[39;49;00m[33m>women is lucky to find a physician who is willing to treat the cause and [39;49;00m[33m\n[39;49;00m[33m>not give give her advise to use the OTC anti-fungal creams.[39;49;00m[33m\n[39;49;00m[33m\n[39;49;00m[33mLucky how?  Since a recent article (randomized controlled trial) of[39;49;00m[33m\n[39;49;00m[33moral yogurt on reducing vaginal candidiasis, I[39;49;00m[33m\'[39;49;00m[33mve mentioned to a [39;49;00m[33m\n[39;49;00m[33mnumber of patients with frequent vaginal yeast infections that they[39;49;00m[33m\n[39;49;00m[33mcould try eating 6 ounces of yogurt daily.  It turns out most would[39;49;00m[33m\n[39;49;00m[33mrather just use anti-fungal creams when they get yeast infections.[39;49;00m[33m\n[39;49;00m[33m\n[39;49;00m[33m>yogurt dangerous).  If this were a standard part of medical practice, as [39;49;00m[33m\n[39;49;00m[33m>Gordon R. says it is, then the incidence of GI distress and vaginal yeast [39;49;00m[33m\n[39;49;00m[33m>infections should decline.[39;49;00m[33m\n[39;49;00m[33m\n[39;49;00m[33mAgain, this just isn[39;49;00m[33m\'[39;49;00m[33mt what the systemic yeast syndrome is about, and[39;49;00m[33m\n[39;49;00m[33mhas nothing to do with the quack therapies that were being discussed.[39;49;00m[33m\n[39;49;00m[33mThere is some evidence that attempts to reinoculate the GI tract with[39;49;00m[33m\n[39;49;00m[33mbacteria after antibiotic therapy don[39;49;00m[33m\'[39;49;00m[33mt seem to be very helpful in[39;49;00m[33m\n[39;49;00m[33mreducing diarrhea, but I don[39;49;00m[33m\'[39;49;00m[33mt think anyone would view this as a[39;49;00m[33m\n[39;49;00m[33mquack therapy.[39;49;00m[33m\n[39;49;00m[33m-- [39;49;00m[33m\n[39;49;00m[33mDavid Rind[39;49;00m[33m\n[39;49;00m[33mrind@enterprise.bih.harvard.edu[39;49;00m[33m\n[39;49;00m[33m'[39;49;00m]
        labels = [[34m2.0[39;49;00m, [34m2.0[39;49;00m]
        
        sc = SeldonClient(
            gateway=[33m"[39;49;00m[33mambassador[39;49;00m[33m"[39;49;00m,
            gateway_endpoint=API_AMBASSADOR,
            deployment_name=[33m"[39;49;00m[33mseldon-model-server[39;49;00m[33m"[39;49;00m,
            payload_type=[33m"[39;49;00m[33mndarray[39;49;00m[33m"[39;49;00m,
            namespace=[33m"[39;49;00m[33mseldon[39;49;00m[33m"[39;49;00m,
            transport=[33m"[39;49;00m[33mrest[39;49;00m[33m"[39;49;00m)
    
        sm_result = sc.predict(data=np.array(data))
        logging.info(sm_result)
        result = seldon_message_to_json(sm_result.response)
        logging.info(result)
        values = result.get([33m"[39;49;00m[33mdata[39;49;00m[33m"[39;49;00m, {}).get([33m"[39;49;00m[33mndarray[39;49;00m[33m"[39;49;00m, {})
        [34massert[39;49;00m (values == labels)


### Now push your changes to trigger the pipeline
Because Jenkins Classic has created a CI GitOps pipeline for our repo we just need to push our changes to run all the tests

We can do this by running our good old git commands:


```bash
%%bash
git add .
git push origin master
```

We can now see that the pipeline has been triggered by viewing our activities:



```python
!jx get activity -f sig-mlops-seldon-jenkins-x | tail
```

        Create Effective Pipeline                          11h28m57s       7s Succeeded 
        Create Tekton Crds                                 11h28m50s      11s Succeeded 
      test and deploy sklearn server                       11h28m38s    1m54s Succeeded 
        Credential Initializer 59hx6                       11h28m38s       0s Succeeded 
        Working Dir Initializer Fslpm                      11h28m38s       1s Succeeded 
        Place Tools                                        11h28m37s       1s Succeeded 
        Git Source Seldonio Sig Mlops Seldon Jenki Ftjtn   11h28m36s       6s Succeeded https://github.com/SeldonIO/sig-mlops-seldon-jenkins-x.git
        Git Merge                                          11h28m30s       1s Succeeded 
        Run Tests                                          11h28m29s      13s Succeeded 
        Build And Push Images                              11h28m16s    1m32s Succeeded 


Similarly we can actually see the logs of our running job:


```bash
%%bash
YOUR_GIT_USERNAME=SeldonIO
jx get build logs "$YOUR_GIT_USERNAME/sig-mlops-seldon-jenkins-x/master #7 release" | tail
```

    error: Failed to parse docker reference ELDON_BASE_WRAPPER
    ERROR: An error occurred: unable to get metadata for ELDON_BASE_WRAPPER:latest
    ERROR: Suggested solution: check image name
    ERROR: If the problem persists consult the docs at https://github.com/openshift/source-to-image/tree/master/docs. Eventually reach us on freenode #openshift or file an issue at https://github.com/openshift/source-to-image/issues providing us with a log from your build using log output level 3.
    Makefile:8: recipe for target 'build' failed
    make: *** [build] Error 1
    Stopping Docker: dockerProgram process in pidfile '/var/run/docker-ssd.pid', 1 process(es), refused to die.
    [31m
    Pipeline failed on stage 'test-and-deploy-sklearn-server' : container 'step-build-and-push-images'. The execution of the pipeline has stopped.[0m
    


    wrote: /tmp/086bfe4e-d4ac-46e6-baa1-71d4ef7abca4095596018


## Managing your Jenkins X Application

Now that we've deployed our MLOps repo, Jenkins X now has created an application from our charts.

This application gets automatically syncd into the Jenkins X staging environment, which you can see:


```python
!kubectl get pods -n jx-staging
```

### Test your application in the staging environment


```python
from seldon_core.seldon_client import SeldonClient
import numpy as np

url = !kubectl get svc ambassador -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

sc = SeldonClient(
    gateway="ambassador", 
    gateway_endpoint="localhost:80",
    deployment_name="mlops-server",
    payload_type="ndarray",
    namespace="jx-staging",
    transport="rest")

response = sc.predict(data=np.array([twenty_test.data[0]]))

response.response.data
```




    ndarray {
      values {
        number_value: 2.0
      }
    }




```bash
%%bash
curl -X POST -H 'Content-Type: application/json' \
     -d "{'data': {'names': ['text'], 'ndarray': ['Hello world this is a test']}}" \
    http://localhost/seldon/jx-staging/news-classifier-server/api/v0.1/predictions
```

    {
      "meta": {
        "puid": "so6n21pkf70fm66eka28lc63cr",
        "tags": {
        },
        "routing": {
        },
        "requestPath": {
          "news-classifier-server-processor": "axsauze/sklearn-server:0.1"
        },
        "metrics": []
      },
      "data": {
        "names": [],
        "ndarray": [2.0]
      }
    }

      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100   350  100   278  100    72   7942   2057 --:--:-- --:--:-- --:--:-- 10294

