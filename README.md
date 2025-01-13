# KAITO Chatbot Sample

![Publish kaitochat image](https://github.com/pauldotyu/kaitochat/actions/workflows/publish-kaitochat.yml/badge.svg)

A sample chatbot built with [Streamlit](https://streamlit.io/) to interact with an open-source model hosted on AKS via [KAITO](https://github.com/kaito-project/kaito). 

To test this app, you need to have an [AKS cluster](https://learn.microsoft.com/azure/aks/learn/quick-kubernetes-deploy-portal?tabs=azure-cli) with KAITO installed.

## Prerequisites

To run this example, you will need the following installed on your development machine:

- [Python3](https://www.python.org/downloads/)
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Helm](https://helm.sh/docs/intro/install/)

## Create AKS cluster and install KAITO

Follow the instructions in the [KAITO documentation](https://github.com/kaito-project/kaito/blob/main/docs/installation.md) to create an AKS cluster and install KAITO.

## Provision a workspace

To provision a phi-3-mini workspace, run the following command.

```bash
kubectl apply -f https://raw.githubusercontent.com/kaito-project/kaito/main/examples/inference/kaito_workspace_phi_3.yaml
```

## Run the app locally

To test the app locally, the app must be able to communicate with the KAITO workspace. To do this, expose the workspace using LoadBalancer service type.

The sample manifest does not include a public IP, however KAITO docs provide instructions for [provisioning a workspace with a public IP](https://github.com/kaito-project/kaito/tree/main/examples).

To add a public IP to an existing workspace, run the following command.

```bash
kubectl patch service workspace-phi-3-mini -p '{"spec":{"type":"LoadBalancer"}}'
```

Wait for the public IP to be provisioned then run the following command to set the environment variables.

```bash
export MODEL_ENDPOINT="http://$(kubectl get svc workspace-phi-3-mini -o jsonpath='{.status.loadBalancer.ingress[0].ip}')/v1/chat/completions"
export MODEL_NAME="phi-3-mini-128k-instruct"
```

Create a virtual environment and install the dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

Run the app.

```bash
streamlit run main.py
```

## Run the app on AKS

To test this app on an AKS cluster, run the following command to deploy the kaito chat demo app in the same AKS cluster that is hosting the workspace.

```bash
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: kaitochatdemo
  name: kaitochatdemo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kaitochatdemo
  template:
    metadata:
      labels:
        app: kaitochatdemo
    spec:
      containers:
      - name: kaitochatdemo
        image: ghcr.io/pauldotyu/kaitochat/kaitochatdemo:latest
        resources: {}
        env:
        - name: MODEL_ENDPOINT
          value: "http://workspace-phi-3-mini:80/v1/chat/completions"
        - name: MODEL_NAME
          value: "phi-3-mini-128k-instruct"
        ports:
        - containerPort: 8501
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: kaitochatdemo
  name: kaitochatdemo
spec:
  type: LoadBalancer
  ports:
  - port: 80
    protocol: TCP
    targetPort: 8501
  selector:
    app: kaitochatdemo
EOF
```

Wait for the public IP to be provisioned then run the following command to get the public IP.

```bash
echo "http://$(kubectl get svc kaitochatdemo -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
```

Click the link that is outputted in the terminal to open the app in your browser.

> [!NOTE]
> Be sure to remove the resources publicly accessible service created in this step after you are done testing the app.

## Clean up

After you are done testing the app, you can follow the instructions in the [KAITO documentation](https://github.com/kaito-project/kaito/blob/main/docs/installation.md#clean-up) to remove the KAITO installation from your AKS cluster and/or [delete the AKS cluster](https://learn.microsoft.com/azure/aks/learn/quick-kubernetes-deploy-portal?tabs=azure-cli#delete-the-cluster).