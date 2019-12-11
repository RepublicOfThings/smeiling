#!/usr/bin/env bash

for dir in */; do
    if [ $(find "$dir" -name "Dockerfile") ]; then
      docker build . -t ${dir%/}:latest -f ${dir%/}/Dockerfile
      # docker tag rhel-httpd registry-host:5000/myadmin/rhel-httpd
      # docker push registry-host:5000/myadmin/rhel-httpd
      docker tag ${dir%/} gcr.io/encoded-antler-258511/${dir%/}
      docker push gcr.io/encoded-antler-258511/${dir%/}
    fi
done
