#!/bin/bash
minikube stop
minikube delete
if [ $? -eq 0 ]
then
    echo "stop OK"
else
    echo "error"
fi