#!/usr/bin/env bash
#
# Prepare use of redis for the live updating demo
#
# Use of docker is not necessary. Alternatives such as a simple sudo apt-get install redis should also work.
# Also, the use of redis is driven by the configuration of the channels project; changing the CHANNEL_LAYERS
# setting will directly impact and even remove the need for redis
#
docker pull redis:4
docker run -p 6379:6379 -d redis
