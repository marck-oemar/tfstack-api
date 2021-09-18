# API to manage Terraform managed resources

## Context
Terraform is great for defining Infrastructure as 'Code', it is an abstraction to infrastructure composition. Just provide
a input parameters and execute a 'terraform apply' to align the infrastructure state with the code.

It also requires the execution of the Terraform binary, in an OS environment (for instance a VM or Container). 
This proof of concept presents an API that is able to represent Terraform deployments as API resources and allows for CRUD operations.

To be clear, this is not production-grade!

## Technology
- Flask
- SwaggerUI
- Celery
- Terraform, Terraform State Workspaces, Terraform Remote State 
- Docker container
- Kubernetes
- AWS, S3

## Design

### API Layer
The API provides resources and methods to (mostly asynchronously) perform operations and retrieve status of requests.
- Technology: 
  - Flask and Flask Blueprint
  - SwaggerUI
  - Celery
- Runtime deployment: Kubernetes Pod deployment, capable of horizontal scaling
- Request routing
- Create a Celery task on incoming request
- Request status management

Celery allows us to decouple the processing of requests from the interface. 

Flask is using the build-in WSGI which is not production-grade.

### Backend/Broker
The Backend/Broker is a datastore responsible for managing requests and results for Celery. 
- Technology: 
  - Redis, single instance. Not production-grade.
- Runtime deployment: Kubernetes service/deployment

### Worker Layer
This is a Celery worker that retrieves and executes Celery tasks, runs in a container, and consists of 2 components.

#### Celery Task Layer
Celery tasks that have a 1-on-1 relation and tight coupling with the Terraform execution layer, specifically CRUD operations.
- Executes retrieved Celery tasks and spawns and manages sub-processes for the Terraform execution scrips. 
- Catch errors from the sub-process

#### Terraform execution layer
Shell scripts have a 1-on-1 relation with the Celery tasks and manage the CRUD operations.
They are specific to the Terraform config and exist within the same Terraform config repository.

- Ability to perform concurrent execution of the Terraform binary in a single container.
- Abstraction for the Terraform logic. All it exposes is CRUD operations. 
- Terraform State workspace management. The 1-to-many relation of a Terraform Config related to multiple Terraform deployments is solved by using Terraform State workspaces. Every new creation of a Terraform 'stack' involves a unique Terraform workspace.
- Generate random resource ID, per new Terraform stack.

#### Terraform config layer
This is the actual Terraform config and resides in a separate repo. 
For this concept I'm using my repo https://github.com/marck-oemar/tf-compute-example which is a AWS EC2 instance deployment.
- AWS EC2 instance
- S3 state backend
- Requires AWS credentials, injected somehow during deployment

## Usage
First clone this repo and the https://github.com/marck-oemar/tf-compute-example repo.

### Requirements
- AWS account with credentials and permissions to create EC2 and IAM resources, defined in the Terraform Config.
- S3 bucket for Terraform Remote State Backend. 
- Kubernetes Cluster, for example Minikube, KIND, EKS etc. 
- Docker Engine

### Configure the Terraform config
In the Terraform config repo, adjust the Terraform Backend S3 config. 

### Build
Since we're deploying Kubernetes objects, Use ```docker build``` build the 2 container images for the App and the Worker, tag and push them to a container registry to your liking, for instance DockerHub

### Deploy in Kubernetes Cluster

Kubernetes deployment is available in manifests and a local helm chart. 
- The images point to my public 'elmoenco' dockerhub registry.
- The Kubernetes deployment expects an ingress controller. 
- We need proper AWS credentials.

First, create a Kubernetes Secret for the AWS credentials: 

```
kubectl create secret generic aws-credentials --from-file=.aws/credentials
```

Deploy:
1. Use ```kubectl apply``` to deploy the Kubernetes manifests or 
2. Or ```helm upgrade --install tfstack-api tfstack-api/``` to install helm chart


### Discover
Access the (ingress endpoint)/swagger to discover and try out the API.


## Test
To execute the unittests:


```
cd src
pip3 install -r requirements.txt
python3 -m unittest discover -v
```


