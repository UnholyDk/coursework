#!/bin/bash
minikube start --vm-driver=virtualbox
minikube status
if [ $? -eq 0 ]
then
    echo "start OK"
else
    echo "error"
fi

./get_volcano.sh
kubectl apply -f queue.yaml
kubectl apply -f persistent_volume.yaml
kubectl apply -f pv-claim.yaml
kubectl proxy --port=8080
