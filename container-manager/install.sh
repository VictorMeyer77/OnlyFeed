#!/bin/bash

# arrêt et suppression conteneur existant
sudo docker stop $(sudo docker ps -a -q)
sudo docker system prune -a -f

# installation cron
sudo apt-get update
sudo apt-get install cron
sudo systemctl enable cron

# lancement cron
sudo /usr/sbin/crond -f -l 8
sudo /usr/bin/crontab crontab.txt

# création des images
sudo docker build -t steam_pipeline ../steam-pipeline/.
sudo docker build -t game_rating ../game-rating/.

# lancement docker-compose
sudo docker-compose -f ../docker-compose.yml up -d
