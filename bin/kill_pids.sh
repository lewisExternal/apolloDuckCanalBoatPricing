#!/bin/bash
echo "Killing the following PIDs..."
ps aux | grep '[m]ain' | awk '{print $2}'
ps aux | grep '[m]ain' | awk '{print $2}' | xargs kill -9