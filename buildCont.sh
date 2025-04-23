#!/bin/bash 

docker buildx build --platform=linux/amd64 -t service-metrics:1.0.0 .
