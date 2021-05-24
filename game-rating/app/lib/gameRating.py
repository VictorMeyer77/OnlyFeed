from .postgresDao import PostgresDao
from nltk.corpus import words, stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import spacy
import sys


class GameRating:

    def __init__(self, confPostgres):

        nltk.download('vader_lexicon')

        self.postgres = PostgresDao(confPostgres)
        self.nlp = spacy.load("en_core_web_lg")
        self.criteraWords = self.getCriteraNlpWords()

    def run(self):

        sid = SentimentIntensityAnalyzer()
        gameIds = self.postgres.getGameIds()

        i = 0
        while i < len(gameIds):

            reviewSentences = self.getAllGameReviewSentence(gameIds[i])
            reviewWordsBySentence = self.getWordsBySentences(reviewSentences)
            usefullWordsBySentence = self.removeUselessWords(reviewWordsBySentence)
            nlpUsefullWordsBySentence = self.getNlpWordsBySentence(usefullWordsBySentence)
            criteraReviewSentences = self.getReviewCriteraSentences(reviewSentences, nlpUsefullWordsBySentence)

            rates = {}
            for k in criteraReviewSentences.keys():
                rates[k] = -1.0

            for k in criteraReviewSentences.keys():
                rates[k] = int((sid.polarity_scores(" ".join(criteraReviewSentences[k]))["compound"] + 1) * 10)

            for rate in rates:

                if rate != 10.0:

                    self.postgres.insertGameRating(gameIds[i], list(rates.values()))
                    break

            i += 1

    def getAllGameReviewSentence(self, gameId):

        reviewText = self.postgres.getGameReviews(gameId)
        reviewSentences = nltk.tokenize.sent_tokenize(reviewText)

        return reviewSentences

    @staticmethod
    def getWordsBySentences(sentences):

        wordsBySentences = []
        for sentence in sentences:
            wordsBySentences.append(sentence.split(" "))

        return wordsBySentences

    @staticmethod
    def removeUselessWords(wordsBySentence):

        clearWords = []
        existWords = words.words()
        sw = set(stopwords.words("english"))

        for wordList in wordsBySentence:

            wordsBuffer = []

            for word in wordList:

                cleanWord = word.lower().replace(".", "").replace(",", "").replace("!", "").replace("?", "")

                if cleanWord not in sw and cleanWord in existWords:
                    wordsBuffer.append(cleanWord)

            clearWords.append(wordsBuffer)

        return clearWords

    def getCriteraNlpWords(self):

        criteraWords = self.postgres.getCriteraWords()
        nlpCritera = {}

        if criteraWords == {}:

            print("ERROR GameRating: Aucun mot clef précisé")
            sys.exit()
        else:

            for k in criteraWords.keys():
                nlpCritera[k] = []

                for word in criteraWords[k]:
                    nlpCritera[k].append(self.nlp(word))

        return nlpCritera

    def getNlpWordsBySentence(self, wordsBySentence):

        nlpWordsBySentence = []

        for wordList in wordsBySentence:

            nlpWordsBuffer = []

            for word in wordList:
                nlpWordsBuffer.append(self.nlp(word))

            nlpWordsBySentence.append(nlpWordsBuffer)

        return nlpWordsBySentence

    def getReviewCriteraSentences(self, reviewSentences, wordsBySentences):

        criteraSentences = {}
        for k in self.criteraWords.keys():
            criteraSentences[k] = []

        for i in range(len(reviewSentences)):

            for k in criteraSentences.keys():

                isCritSentence = False

                for criteraWord in self.criteraWords[k]:

                    if isCritSentence:
                        break

                    for word in wordsBySentences[i]:

                        if isCritSentence:
                            break

                        if criteraWord.similarity(word) > 0.5:
                            criteraSentences[k].append(reviewSentences[i])
                            isCritSentence = True

        return criteraSentences
