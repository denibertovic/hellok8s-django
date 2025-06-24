#!/bin/bash

# Add docker group
groupadd docker --gid ${DOCKER_GROUP_ID:-129}

# Add local user
# Either use the LOCAL_USER_ID if passed in at runtime or
# fallback
# The user is added to the docker group to be able to start containers
# if necessary for ceartain use cases.

USER_ID=${LOCAL_USER_ID:-9001}

echo "Starting with UID : $USER_ID"
useradd --shell /bin/bash -G ${DOCKER_GROUP_ID:-129} -u $USER_ID -o -c "" -m user
export HOME=/home/user

chown user:user /app -R

exec /sbin/pid1 -u user -g user "$@"
