#!/bin/bash
minikube stop
if [ $? -eq 0 ]
then
    echo "stop OK"
else
    echo "error"
fi