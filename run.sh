#!/bin/bash

default_cmd="python /underling/main.py"

if [ $# -eq 0 ]; then
  cmd="$default_cmd"
else
  cmd="$@"
fi

docker run -it --env-file .env \
           -v "$(pwd)/projects:/projects" \
           -v "$(pwd)/underling:/underling" \
           paulbatum/underling sh -c "$cmd"