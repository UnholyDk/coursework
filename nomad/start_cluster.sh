#!/bin/bash

nomad agent -config server.hcl &
nomad agent -config client1.hcl &
nomad agent -config client2.hcl &
nomad agent -config client3.hcl &
