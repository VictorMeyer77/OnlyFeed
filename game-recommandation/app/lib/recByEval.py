from sklearn.preprocessing import normalize
from sklearn.neighbors import DistanceMetric
from .dataFormater import cleanGameData
import numpy as np
from random import randint

class RecByEval:

    def __init__(self, postgresDao, modelManager):

        self.postgresDao = postgresDao
        self.modelManager = modelManager

    def run(self, nbPredictByUser):

        dictData = self.postgresDao.getGameDataset()
        dataset = cleanGameData(dictData)
        print("INFO: Comparaison de {} jeux.".format(len(dataset[0])))

        model, modelName = self.modelManager.model, self.modelManager.modelName
        print("INFO: Meilleur modèle: {}.".format(modelName))

        pred = self.getModelPred(model, dataset)
        distancePerGroup = self.distancePerGroup(dataset, pred)
        print("INFO: Distance par groupe: {}.".format(distancePerGroup))

        userIds = self.postgresDao.getOfUserId()
        evals = self.postgresDao.getGameUserEvaluation()
        print("INFO: Traitement des {0} utilisateurs et {1} évaluations.".format(len(userIds), len(evals["game_id"])))

        for userId in userIds:

            userEvals = self.getUserGameEval(userId, evals)
            print("INFO: Traitement des {0} évaluations de l'utilisateur {1}.".format(len(userEvals), userId))

            if len(userEvals) < 1:

                randomCat = self.getRandomCat(distancePerGroup, [-1])
                gamesPred = self.getGamesByCat(dataset, pred, nbPredictByUser, randomCat, [])
                print("INFO: Catégorie aléatoire {0} pour l'utilisateur {1}".format(randomCat, userId))

                for gamePred in gamesPred:
                    self.postgresDao.insertGameRecommandation(gamePred, userId)

            else:

                categoriesSumRates = dict.fromkeys(distancePerGroup, 0.0)
                categoriesGamesId = {key: list([]) for key in distancePerGroup.keys()}
                categoriesTargetDist = dict.fromkeys(distancePerGroup, 0.0)

                for userEval in userEvals:
                    gameEvalCat = self.getGameCat(dataset, pred, userEval[0])
                    categoriesSumRates[gameEvalCat] += userEval[1]
                    categoriesGamesId[gameEvalCat].append(userEval[0])

                for k in categoriesGamesId.keys():
                    avg = categoriesSumRates[k] / len(categoriesGamesId[k]) if len(categoriesGamesId[k]) > 0 else 0.0
                    categoriesTargetDist[k] = (10.0 - avg) / 10.0

                sortCat = dict(sorted(categoriesTargetDist.items(), key=lambda item: item[1]))
                print("INFO: Distances par categorie pour l'utilisateur {0}: {1}.".format(userId, sortCat))

                tmpCat = list(sortCat.keys())[0]

                if sortCat[tmpCat] < 0.1:

                    userCat = tmpCat

                else:

                    minDist = abs(sortCat[tmpCat] - distancePerGroup[tmpCat][0])
                    minCat = 0

                    for k in list(distancePerGroup[tmpCat].keys())[1:]:

                        if k != tmpCat and abs(sortCat[tmpCat] - distancePerGroup[tmpCat][k]) < minDist:
                            minDist = sortCat[tmpCat]
                            minCat = k

                    userCat = minCat

                print("INFO: Categorie de l'utilisateur {0}: {1}.".format(userId, userCat))

                banGameId = []
                for userEval in userEvals:
                    banGameId.append(userEval[0])

                gamesPred = self.getGamesByCat(dataset, pred, nbPredictByUser, userCat, banGameId)

                for gamePred in gamesPred:
                    self.postgresDao.insertGameRecommandation(gamePred, userId)

    @staticmethod
    def getModelPred(model, dataset):

        formatData = dataset[1:, :].T
        normData = normalize(formatData, axis=0)
        pred = model.fit_predict(normData)

        return pred

    @staticmethod
    def getGameCat(dataset, pred, gameId):

        for i in range(len(pred)):

            if int(dataset[0][i]) == gameId:
                return pred[i]

        return None

    @staticmethod
    def getRandomCat(dictCat, banCat):

        categories = list(dictCat.keys())
        k = categories[randint(0, len(categories) - 1)]

        if len(categories) == len(banCat):
            print("WARNING: Aucune nouvelle catégorie à retourner. -1")
            return -1

        while k in banCat:
            k = categories[randint(0, len(categories) - 1)]

        return k

    @staticmethod
    def getGamesByCat(dataset, pred, nbGame, cat, banIds):

        gameIds = []

        if len(pred) == len(banIds):
            print("WARNING: Aucun nouveau jeu à retourner. []")
            return []

        i = 0
        while i < len(pred) and len(gameIds) < nbGame:

            if pred[i] == cat:

                if int(dataset[0][i]) not in banIds and int(dataset[0][i]) not in gameIds:
                    gameIds.append(int(dataset[0][i]))

            i += 1

        return gameIds

    @staticmethod
    def getUserGameEval(userId, evals):

        userEvals = []

        for i in range(len(evals["of_user_id"])):

            if evals["of_user_id"][i] == userId:
                userEvals.append((evals["game_id"][i], evals["rate"][i]))

        return userEvals

    @staticmethod
    def distancePerGroup(dataset, pred):

        distancesCountPerClass = {}
        unique, counts = np.unique(pred, return_counts=True)

        for classe in unique:

            distancesCountPerClass[classe] = {}

            for distClasse in unique:
                distancesCountPerClass[classe][distClasse] = 0

        normData = normalize(dataset[1:, :].T, axis=0)
        distanceCalc = DistanceMetric.get_metric("minkowski")
        distances = distanceCalc.pairwise(normData)

        for i in range(distances.shape[0]):

            minDist, ind = 10000.0, -1

            for j in range(distances.shape[0]):

                if i == j or pred[i] == pred[j] or pred[j] == -1:
                    continue

                if distances[i][j] < minDist:
                    minDist = distances[i][j]
                    ind = j

            distancesCountPerClass[pred[i]][pred[ind]] += 1

        for i in distancesCountPerClass.keys():

            tot = sum(list(distancesCountPerClass[i].values()))

            for j in distancesCountPerClass[i].keys():
                distancesCountPerClass[i][j] = float(distancesCountPerClass[i][j]) / tot

        return distancesCountPerClass
