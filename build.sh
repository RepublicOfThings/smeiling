#!/usr/bin/env bash

for dir in */; do
    if [ $(find "$dir" -name "Dockerfile") ]; then
      docker build . -t ${dir%/}:latest -f ${dir%/}/Dockerfile
      docker tag ${dir%/} rothub/${dir%/}
      docker push rothub/${dir%/}
    fi
done
