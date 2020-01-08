readme:
	jupyter nbconvert README.ipynb --to markdown

train_model: install_dev
	cd src && python train_model.py

test:
	cd src && \
		pytest -s --verbose -W ignore --log-level=INFO 2>&1

install_dev:
	pip install -r src/requirements.txt

# INTEGRATION TESTS
install_integration_dev:
	pip install -r integration/requirements-dev.txt

test_integration:
	(cd integration && \
		pytest -s --verbose -W ignore --log-level=INFO 2>&1)

deploy_model:
	kubectl apply -f charts/SeldonDeployment-news-classifier.json -n seldon 
	kubectl rollout status -n seldon deployment/news-classifier-default-cbb4caa

delete_model:
	kubectl delete sdep news-classifier

helm_setup:
	helm repo add stable https://kubernetes-charts.storage.googleapis.com/
	helm repo add seldonio https://storage.googleapis.com/seldon-charts/
	helm repo update

install_ambassador:
	helm install ambassador \
		stable/ambassador \
		-f integration/ambassador_values.yaml \
		--set crds.keep=false \
		--namespace seldon \
		--set replicaCount=1
	kubectl rollout status deployment.apps/ambassador \
		--namespace seldon

install_seldon:
	# We install SC v0.5.1 because there is a bug in v1.0.0
	# which breaks the install with Helm v2.x.
	# https://github.com/SeldonIO/seldon-core/issues/1299
	helm install seldon-core-operator \
		seldonio/seldon-core-operator \
		--namespace seldon \
		--version 0.5.1
	kubectl rollout status -n seldon deployment/seldon-controller-manager

create_namespaces:
	kubectl create namespace seldon || echo "Namespace seldon already exists"
	kubectl config set-context $$(kubectl config current-context) --namespace=seldon

kind_setup: helm_setup install_ambassador install_seldon create_namespaces deploy_model

kind_create_cluster:
	kind create cluster --config integration/kind_config.yaml

kind_delete_cluster:
	kind delete cluster


