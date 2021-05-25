from .postgresDao import PostgresDao
from datetime import datetime
import requests
import json


class GameReviewAlim:

    def __init__(self, confSteamLink, confPostgres):

        self.review_link = confSteamLink["game_review_link"]
        self.postgres = PostgresDao(confPostgres)

    def run(self, count, occurenceByGame):

        flags = self.postgres.getGameFlags()

        for i in range(0, count):

            print("INFO: recherche des commentaires de {}.".format(flags["id"][i]))

            reviews, nextCursor = self.getSteamGameReviews(flags["id"][i], flags["cursor"][i])

            for j in range(0, occurenceByGame):

                if j == occurenceByGame - 1 or reviews is None or \
                        len(reviews) < 1 or nextCursor is None:

                    self.postgres.updateFlag(flags["id"][i], nextCursor)
                    break

                if reviews is not None and len(reviews) > 0:

                    for review in reviews:
                        frmtReview = self.formatGameReview(review, flags["id"][i])
                        self.postgres.insertGameReview(frmtReview)

                reviews, nextCursor = self.getSteamGameReviews(flags["id"][i], nextCursor)

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
