#!/bin/bash
kubectl apply -f https://raw.githubusercontent.com/volcano-sh/volcano/master/installer/volcano-development.yaml

if [ $? -eq 0 ]
then
    echo "volcano OK"
else
    echo "error"
fi