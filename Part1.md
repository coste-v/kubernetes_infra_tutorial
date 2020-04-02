# Part 1 : cluster set up, redis server and redis feeder

## Objectives

- setting up a testing context on our cluster
- get familiar with kubectl command
- understanding Pods and Service
- deploy local container on kubernetes

## A. Cluster set up

### Discovering the cluster

Docker desktop allows you to create a single node kubernetes cluster. Once your cluster is up and running, we can check its configuration using :

```bash
kubectl cluster-info
```

Which outputs :

![Cluster Info](images/part1/cluster-info.png)

Here, we can see the Kubernetes master single node and the KubeDNS (which we won't cover here).

### Namespace

To start our tutorial, we are going to create a namespace in our single node cluster. A namespace is an isolated space in the cluster. We'll experiment in the namespace, and once done, we can delete it with all its ressources, leaving our cluster clean.

To create a namepsace, we are going to run the following command :

```bash
kubectl apply -f kubernetes_files/part1/0_namespace_tutorial.yml
```

```yml
# kubernetes_files/part1/0_namespace_tutorial.yml

apiVersion: v1
kind: Namespace
metadata:
  name: test
  labels:
    name: test
```

To check if everything is fine, we can run the following command :

```bash
kubectl get namespace
```

which outputs :

![Get namespace](images/part1/get-namespace.png)

We can see our that our tutorial-namespace has been created.

### Context

To use our namespace automatically, we are going to create a context. This part could be skipped because we could pass an extra parameters to the kubeclt command to specify in which namespace we want to run it. For instance :

```bash
kubectl apply -f file.yml --namespace=tutorial-namespace
```

A Kubernetes context represents the triplet Cluster + User + Namespace. On docker desktop, we have one cluster (docker-desktop) and one user (docker-desktop). We are going to use them with our namespace to create our tutorial-context :

```bash
kubectl config set-context tutorial-context --namespace=tutorial-namespace --cluster=docker-desktop --user=docker-desktop
```

To see if our context is created, let's run the following command :

```bash
kubectl config view
```

Wich outputs :

![context](images/part1/context.png)

We can see our tutorial-context

We now need to switch our current context to the one we just created. Let's see our current context :

```bash
kubectl config current-context
```

Which outputs "docker-desktop" in my case. Let's change our context with the following command :

```bash
kubectl config use-context tutorial-context
```

Now, everytime we'll run a kubectl command, it will apply it to our current-context, using our tutorial-namespace. Great ! Let's move on and start playing with our cluster.

## B. Starting a redis server

We'll now start our redis server. For the sake of comprehension, we'll run almost everything using the notion of Pod. We'll move on later to more complicated concept.

A Pod is the atomic element in a kubernetes cluster. Our first pod will simply run a redis server. Here is what the configuration file looks like :

```yml
# kubernetes_files/part1/1_pod_redis.yml

apiVersion: v1
kind: Pod  # resource type (Pod, Service, Volume, ...) 
metadata:
  name: redis-server
  labels:
    app: redis  # label to make the service work
spec:
  containers:
    - name: redis-server
      image: redis:alpine3.10
```

Let's explain a bit the configuration !

This yaml file describe a Pod resource. We need to give the ressource a name and optionnally, we can give it some labels.

Here, we chose to label our pod with an app label having the value "redis". This will be useful a bit later.

Finally, we have some info about the containers we would like to run in our Pod. Here we are running a single container instanciating a redis:alpine3.10 image.

Let's run this ressource and see what happens !

```bash
kubectl apply -f kubernetes_files/part1/1_pod_redis.yml
```

If we go on K9s, we can see our redis server up and running :

![redis-server](images/part1/redis-server.png)

Ok, let's interact with our Pod to get a shell inside it and run some redis command :

```bash
kubectl exec -it redis-server -- /bin/sh
```

And once inside our Pod:

![inside-redis-server](images/part1/inside-redis-server.png)

Awesome ! Everything seems to work as expected ! Next step : use the redis_feeder code to populate the redis data base.

## C. The redis feeder

Before describing our redis feeder Pod, we need to build an image of this code. Remember : we would like to work locally.

Let's go in the code/redis_feeder folder and run the following command :

```bash
docker build . -t redis_feeder
```

Let's try to run it to see if everything works fine :

```bash
docker run redis_feeder John Doe
```

Which outputs the following error :

```bash
Not possible to connect to redis-server:6379
```

This error is "normal": we are running our code in docker (so outside our kubernetes cluster) and there are no redis servers available for our redis_feeder. Let's have a quick look at what the code is trying to do :

```python
args = parser.parse_args()

first_name = args.first_name
last_name = args.last_name
environment = os.getenv("ENVIRONMENT", "dev")

redis = Redis(
    host="redis-service",  # Which host to find the redis-server
    port=4321  # Which port to find the redis-server
)

try:
    redis.set("first-name", first_name)
    redis.set("last-name", last_name)
    redis.set("environment", environment)
except ConnectionError:
    print("Not possible to connect to redis-server:6379")
    exit(1)

exit(0)
```

Our code is trying to connect to a redis server on the "redis-service" host using the port 4321. Once connected, it sets value for different variables (first-name, last-name and environment).

Hint : the host and port values are important ;-) !

Ok, let's try to deploy our redis feeder in our brand new kubernetes cluster ! Here is the Pod resource :

```yml
# kubernetes_files/part1/3_pod_feeder.yml

apiVersion: v1
kind: Pod
metadata:
  name: redis-feeder
spec:
  containers:
    - name: redis-feeder
      image: redis_feeder:latest
      imagePullPolicy: Never  # Use local image
      args: ["Cerebral", "Bore"]  # Random arguments
      env:
        - name: ENVIRONMENT
          value: "preproduction"  # Environment variable
  restartPolicy: OnFailure  # To avoid Kubernetes to keep the Pod retrying
```

This resource is a bit different from our redis server one. We have :

- some arguments and an environment variable
- set the imagePullPolicy to "Never". This allows us to use local image. Otherwise, kubernetes will try to find the redis feeder on Dockerhub and will fail (I didn't put this code on Dockerhub).
- set the restartPolicy to "OnFailure". Kubernetes expect our Pod to be up and running. Otherwise, it tries to relaunch them. However our redis feeder is a task that dies once it has set some values in redis. We don't want to have Kubernetes retrying to launch this Pod.

Let's run the resource :

```bash
kubectl apply -f kubernetes_files/part1/3_pod_feeder.yml
```

and see what happens on K9s :
![redis-feeder-K9s-error](images/part1/redis-feeder-K9s-error.png)

There is an error ! But what happened ? Let's figure out !

We can press "Enter" key on K9s to navigate to the logs or use the kubectl command :

```bash
kubectl logs redis-feeder
```

The output is clear :

```bash
Not possible to connect to redis-server:6379
```

The good news is that we ran our Pod in kubernetes ! Yay ! However we do not have our intended outcome... Why ?

Because the redis-feeder cannot reach the redis-server. The redis-server runs in a Pod with unpredictable host and port...

How are we going to tell to the redis-server Pod to expose it's port and fix a host ? By using a Service !

## C. Introducing kubernetes service

What is a service ? A service is a special resource that allows communication between Pods. Let's have a look at our service configuration :

```yml
# kubernetes_files/part1/2_service_redis.yml

apiVersion: v1
kind: Service
metadata:
  name: redis-service  # The host : same value in redis_feeder python code !
spec:
  ports:
  - port: 4321  # The port : same value in redis_feeder python code !
    targetPort: 6379 # The default redis port
  selector:
    app: redis  # Which pods are concerned
```

What happens here ? Kubernetes will create a resource that will allow **any Pods** with the "redis" label (our redis-server has it !) to be accessible with the "redis-service" host name. The service will also redirect the trafic on port 4321 to the port 6379 of any Pods with the "redis" label.

Let's run again our redis_feeder Pod ! But before that, we need to delete the existing one (it terminated but still exists !). This is a little pain in the butt : each time you run a Pod, you need to delete it to run another "version" of it.

To delete the Pod :

```bash
kubectl delete pod redis-feeder
```

Then :

```bash
kubectl apply -f kubernetes_files/part1/3_pod_feeder.yml
```

This time if you connect back to our redis-server, we can see that the values are set accordingly to our pod_feeder.yml file :

```bash
kubectl exec -it redis-server -- /bin/sh
```

![inside-redis-server2](images/part1/inside-redis-server2.png)

Awesome ! We are now done for part 1 ! Let's move on to part 2 and try to consolidate our redis server !
