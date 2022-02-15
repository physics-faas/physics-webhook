# physics-webhook
Webhook for the PHYSICS EU project

## How to use

* First build the image of the webhook (or use the one I already created at
  docker.io/luis5tb/physics-webhook) and push it to your repo:

```
podman build -t docker.io/luis5tb/physics-webhook .
podman push docker.io/luis5tb/physics-webhook
```

* Run ssl.sh script to generate the tls certs. Adapt the APP and NAMESPACE vars
  as needed

```
./ssl.sh
```

* Create the TLS secret or copy the information into the 002-webhook-secret.yaml
```
kubectl create secret tls ${APP}-secret --key=${APP}.key --cert=${APP}.pem
--dry-run=client -o yaml | kubectl apply -f -
```

* Create the resources:

```
kubectl apply -f 001-service.yaml
kubectl apply -f 002-webhook-secret.yaml (only if tls secret not created in
previous step)
kubectl apply -f 003-admission-controller.yaml
kubectl apply -f 004-webhook.yaml
```
