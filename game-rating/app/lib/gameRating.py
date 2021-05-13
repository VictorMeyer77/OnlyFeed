from .postgresDao import PostgresDao
from textblob import TextBlob
import nltk
import spacy
import sys


class GameRating:

    def __init__(self, confPostgres):

        self.postgres = PostgresDao(confPostgres)
        self.nlp = spacy.load("en_core_web_sm")

        self.criteraWords = self.postgres.getCriteraWords()
        if self.criteraWords == {}:
            print("ERROR GameRating: Aucun mot clef précisé")
            sys.exit()

    def run(self, nbGame):

        gameIds = self.postgres.getGameIds()

        i = 0
        while i < nbGame and i < len(gameIds):

            reviewSentences = self.getAllGameReviewSentence(i)
            criteraReviewSentences = self.getReviewCriteraSentences(reviewSentences)

            rates = {}
            for k in criteraReviewSentences.keys():
                rates[k] = -1.0

            for k in criteraReviewSentences.keys():
                rates[k] = int((TextBlob(" ".join(criteraReviewSentences[k])).sentiment[0] + 1.0) * 10.0)

            i += 1

    def getAllGameReviewSentence(self, gameId):

        reviewText = self.postgres.getGameReviews(gameId)
        reviewSentences = nltk.tokenize.sent_tokenize(reviewText)

        return reviewSentences

    def getReviewCriteraSentences(self, reviewSentences):

        criteraSentences = {}
        for k in self.criteraWords.keys():
            criteraSentences[k] = []

        for reviewSentence in reviewSentences:

            for k in criteraSentences.keys():

                isCritSentence = False

                for criteraWord in self.criteraWords[k]:

                    nlpCW = self.nlp(criteraWord)

                    for reviewWord in reviewSentence.split(" "):

                        if not isCritSentence and nlpCW.similarity(self.nlp(reviewWord)) > 0.87:
                            criteraSentences[k].append(reviewSentence)
                            isCritSentence = True

        return criteraSentences
