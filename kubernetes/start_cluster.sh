#!/bin/bash
minikube start --vm-driver=virtualbox
minikube status
if [ $? -eq 0 ]
then
    echo "start OK"
else
    echo "error"
fi