#!/bin/bash
echo "start random commit task..."
> run.log
python3 ./randomcommit.py > run.log & 
