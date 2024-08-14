#!/bin/bash
set -e

rm -f portfolio-roast.tar
sudo docker build -t portfolio-roast .
sudo docker save portfolio-roast:latest -o portfolio-roast.tar
sudo chmod 777 ./portfolio-roast.tar