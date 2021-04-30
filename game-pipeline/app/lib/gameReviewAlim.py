from kafka import KafkaProducer
from psycopg2 import pool
from datetime import datetime
from random import randint
import requests
import json
import sys
import time


class GameReviewAlim:

    def __init__(self, confSteamLink, confPostgres, confKafka):

        self.review_link = confSteamLink["game_review_link"]
        self.kafkaHost = confKafka["host"]
        self.kafkaPort = confKafka["port"]
        self.kafkaTopics = confKafka["topics"]

        try:

            self.pool = pool.SimpleConnectionPool(1, 10, host=confPostgres["host"],
                                                  port=confPostgres["port"],
                                                  dbname=confPostgres["database"],
                                                  user=confPostgres["user"],
                                                  password=confPostgres["password"])

        except Exception as e:

            print("ERROR: Impossible de se connecter à la base de données")
            print(e)
            sys.exit()

    def run(self, count):

        flags = self.getGameFlags()

        i = 0

        while i < count:

            reviews = self.getSteamGameReviews(flags["id"][i], flags["cursor"][i])

            if reviews is not None and len(reviews) > 0:

                for review in reviews:
                    frmtReview = self.formatGameReview(review, flags["id"][i])
                    self.sendToTopic(frmtReview)

            else:
                count += 1

        i += 1

    @staticmethod
    def formatGameReview(review, gameId):

        return {"id": review["recommendationid"],
                "author_id": review["author"]["steamid"],
                "game_id": gameId,
                "date_create": str(datetime.fromtimestamp(review["timestamp_created"])),
                "review": review["review"]}

    # STEAM

    def getSteamGameReviews(self, gameId, flag):

        gameReviewRequest = requests.get(self.review_link.formta(str(gameId), flag))
        gameReviewResult = json.loads(gameReviewRequest.content)

        if gameReviewResult["success"] == 1:
            return gameReviewResult["reviews"]
        else:
            return None

    # POSTGRES

    def getGameFlags(self):

        try:

            flags = {"id": [], "cursor": []}
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("select game_id, flag from steam_game_reviews_flag order by date_maj")
            resultReq = cursor.fetchall()

            for res in resultReq:
                flags["id"].append(res[0])
                flags["cursor"].append(res[1])

            cursor.close()
            conn.close()
            return flags

        except Exception as e:

            print("ERROR getReviewFlags: " + str(e))
            sys.exit()

    # KAFKA

    def sendToTopic(self, review):

        try:

            producer = KafkaProducer(bootstrap_servers="{}:{}".format(self.kafkaHost, self.kafkaPort))
            producer.send(self.kafkaTopics[randint(0, len(self.kafkaTopics)), json.dumps(review).encode()])
            time.sleep(0.5)

        except Exception as e:

            print("ERROR sendToTopic: " + str(e))
