#!/bin/bash

kill $(ps | grep "nomad agent" | awk '{print $1}')