#!/bin/bash

kill $(ps aux | grep "nomad agent" | awk '{print $1}')