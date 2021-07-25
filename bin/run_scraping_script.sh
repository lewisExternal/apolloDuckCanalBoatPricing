#!/bin/bash

function activate {
            source env/bin/activate
}

if [ ! -d "./env" ];
then

    echo "Creating environment..."
    python3.8 -m venv env
    activate
    python3.8 -m pip install -r ./requirements.txt

else

    echo "Environment already exists"
    activate

fi
    ./kill_pids.sh
    echo "Script will be run in the background. Please run: watch tail ../logs/scraping_log.txt"
    nohup python3.8 -u ../src/scraping/main.py $1 >> ../logs/scraping_log.txt 2>&1 &

deactivate