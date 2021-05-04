from psycopg2 import pool
from datetime import datetime
import requests
import json
import sys


class GameReviewAlim:

    def __init__(self, confSteamLink, confPostgres):

        self.review_link = confSteamLink["game_review_link"]

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

        occurenceByGame = 1 if int(len(flags["id"]) / count) < 1 else int(len(flags["id"]) / count)

        for i in range(0, len(flags["id"])):

            for j in range(0, occurenceByGame):

                reviews, nextCursor = None, None

                if j == 0:

                    reviews, nextCursor = self.getSteamGameReviews(flags["id"][i],
                                                                   flags["cursor"][i])

                else:

                    reviews, nextCursor = self.getSteamGameReviews(flags["id"][i],
                                                                   nextCursor)

                if j == occurenceByGame - 1:

                    self.updateFlag(flags["id"][i], nextCursor)

                if reviews is not None and len(reviews) > 0:

                    for review in reviews:

                        frmtReview = self.formatGameReview(review, flags["id"][i])
                        self.insertGameReview(frmtReview)

    @staticmethod
    def formatGameReview(review, gameId):

        return (review["recommendationid"],
                review["author"]["steamid"],
                gameId,
                str(datetime.fromtimestamp(review["timestamp_created"])),
                review["review"])

    # STEAM

    def getSteamGameReviews(self, gameId, flag):

        gameReviewRequest = requests.get(self.review_link.format(str(gameId), flag))
        gameReviewResult = json.loads(gameReviewRequest.content)

        if gameReviewResult["success"] == 1:

            return gameReviewResult["reviews"], gameReviewResult["cursor"]

        else:
            return None, None

    # POSTGRES

    def getGameFlags(self):

        try:

            flags = {"id": [], "cursor": []}
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT game_id, flag FROM steam_game_reviews_flag ORDER BY date_maj")
            resultReq = cursor.fetchall()

            for res in resultReq:
                flags["id"].append(res[0])
                flags["cursor"].append(res[1])

            self.pool.putconn(conn)
            return flags

        except Exception as e:

            print("ERROR getGameFlags: " + str(e))

    def insertGameReview(self, review):

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO steam_game_reviews"
                           " (id, author_id, game_id, date_create, review)"
                           " VALUES (%s, %s, %s, %s, %s)", review)
            conn.commit()
            self.pool.putconn(conn)

        except Exception as e:

            print("ERROR insertGameReview: " + str(e))

    def updateFlag(self, gameId, flag):

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            now = str(datetime.now())
            cursor.execute("UPDATE steam_game_reviews_flag SET flag = %s, date_maj = %s WHERE game_id = %s",
                           (flag, now, gameId))

            conn.commit()
            self.pool.putconn(conn)

        except Exception as e:

            print("ERROR insertGameReview: " + str(e))
