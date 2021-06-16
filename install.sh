#!/bin/bash

# arrêt et suppression conteneur existant
sudo docker stop $(sudo docker ps -a -q)
sudo docker system prune -a -f

# installation cron
sudo apt-get update
sudo apt-get install cron
sudo systemctl enable cron

# ajout recommandation
cp crontab.txt newcron.txt
echo "0 15 * * * sudo docker run -v $(pwd)/volumes/models:/models -d game_recommandation:latest python /app/main.py genrec 10" >> newcron.txt
echo "0 15 * * 5 sudo docker run -v $(pwd)/volumes/models:/models -d game_recommandation:latest  python /app/main.py genmod 10 100" >> newcron.txt

# lancement cron
sudo /usr/sbin/crond -f -l 8
sudo /usr/bin/crontab newcron.txt
rm newcron.txt

# création des images
sudo docker build -t steam_pipeline steam-pipeline/.
sudo docker build -t game_rating game-rating/.
sudo docker build -t game_recommandation game-recommandation/.

# lancement docker-compose
sudo docker-compose -f docker-compose.yml up -d
