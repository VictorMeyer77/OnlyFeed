from .postgresDao import PostgresDao
import nltk

class GameRating:

    def __init__(self, confPostgres):

        self.postgres = PostgresDao(confPostgres)

        self.getAllGameReviewSentence(400)

    def getAllGameReviewSentence(self, gameId):

        reviewText = self.postgres.getGameReviews(gameId)
        reviewSentences = nltk.tokenize.sent_tokenize(reviewText)
        print(reviewSentences)
