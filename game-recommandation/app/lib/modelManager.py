from .dataFormater import cleanGameData
from .model import Model
from random import randint
from time import sleep
import numpy as np


class ModelManager:

    def __init__(self, postgresDao, modelType, confModels, outputDir):

        self.postgresDao = postgresDao
        self.modelType = modelType
        self.confModels = confModels
        self.nearestNeightboor = confModels["defaultNearestNeightboor"]
        self.alpha = confModels["defaultAlpha"]
        self.minGameByCat = confModels["defaultMinGameByCat"]
        self.outputDir = outputDir
        self.model, self.modelName = self.chooseModels()

    def chooseModels(self):

        models = self.postgresDao.getModels(self.modelType)
        trainer = Model(self.modelType, self.nearestNeightboor, self.alpha, self.minGameByCat, self.outputDir,
                        self.postgresDao, True)

        print("INFO: {0} modèles de type {1}.".format(len(models["name"]), self.modelType))

        dictData = self.postgresDao.getGameDataset()
        dataset = cleanGameData(dictData)

        print("INFO: Dataset composé de {} jeux.".format(len(dataset[0, :])))

        simTests = self.postgresDao.getGameTestSimilarityResult()

        if len(models["name"]) < 1:

            print("INFO: Entrainement du modèle par défault...")
            trainer.train(dataset)
            model = trainer.loadModel("default")
            modelName = "default"

        elif len(simTests["id_game_test"]) < 1:

            model = trainer.loadModel("default")
            modelName = "default"

        else:

            print("INFO: Sélection du meilleur modèles entre {} modèles.".format(len(models["name"])))

            modelRates = {}


            print("INFO: {} tests de similarité.".format(len(simTests["id_game_test"])))

            for i in range(len(models["name"])):
                model = trainer.loadModel(models["name"][i])
                modelRates[models["name"][i]] = self.evluateModel(trainer, model, dataset, simTests)
                print("INFO: Evaluation du modèle {}: {}.".format(models["name"][i], modelRates[models["name"][i]]))

            orderRates = dict(sorted(modelRates.items(), key=lambda item: item[1], reverse=True))

            if len(models["name"]) > 100:

                print("INFO: nettoyage des modèles, conservation des 50 meilleurs...")

                for k in list(orderRates.keys())[50:]:

                    if k != "default":
                        trainer.dropModel(k)
                        self.postgresDao.deleteModel(k)
                        print("INFO: Supression du modèle {}".format(orderRates[k]))

            modelName = list(orderRates.keys())[0]
            model = trainer.loadModel(list(orderRates.keys())[0])

            print("INFO: Meilleur modèle: {}, note {}.".format(modelName, orderRates[modelName]))

        return model, modelName

    def trainNewModels(self, nbModel):

        existModels = self.postgresDao.getModels(0)
        print("INFO: {0} modèles de type {1}.".format(len(existModels["name"]), self.modelType))

        dictData = self.postgresDao.getGameDataset()
        dataset = cleanGameData(dictData)
        print("INFO: Dataset composé de {} jeux.".format(len(dataset[0, :])))

        newModels = []

        while len(newModels) < nbModel:

            if len(existModels) + len(newModels) >= \
                    (self.confModels["nearestNeightboor"][1] - self.confModels["nearestNeightboor"][0]) / \
                    self.confModels["nearestNeightboor"][2] \
                    + (self.confModels["alpha"][1] - self.confModels["alpha"][0]) / self.confModels["alpha"][2] \
                    + (self.confModels["minGameByCat"][1] - self.confModels["minGameByCat"][0]) / \
                    self.confModels["minGameByCat"][2]:

                print("WARNING: Plus aucune combinaison de paramètres possible")
                break

            else:

                newModel = self.getRandomParam()
                if not self.isParamAlreadyExist(newModel, existModels):
                    newModels.append(newModel)

        print("INFO: Entrainement de {} nouveaux modèles...".format(len(newModels)))

        for newModel in newModels:
            print("INFO: Entrainement {}.".format(newModel))

            trainer = Model(self.modelType, newModel[0], newModel[1], newModel[2], self.outputDir,
                            self.postgresDao, False)
            trainer.train(dataset)
            sleep(1)

    def generateGameTestSimilarity(self, nbTest):

        dictData = self.postgresDao.getGameDataset()
        dataset = cleanGameData(dictData)

        if len(dataset[0]) < 5:
            print("ERROR: Trop peu de jeux ({}) pour générer un test de similarité.".format(len(dataset[0])))

        for i in range(nbTest):
            testGameIds = np.random.choice(dataset[0], 4)
            self.postgresDao.insertGameTestSimilarity(int(testGameIds[0]), int(testGameIds[1]),
                                                      int(testGameIds[2]), int(testGameIds[3]))

            print("INFO: Insertion test similarté: {} - {} - {} - {}"
                  .format(int(testGameIds[0]), int(testGameIds[1]), int(testGameIds[2]), int(testGameIds[3])))

    @staticmethod
    def evluateModel(trainer, model, dataset, similarityTests):

        model, pred = trainer.clusterize(dataset, model)
        gameIds = dataset[0, :]

        rate = 0.0
        nbTest = 0

        for i in range(len(similarityTests["result"])):

            indexTest = np.where(gameIds == similarityTests["id_game_test"][i])[0]
            indexOne = np.where(gameIds == similarityTests["id_game_one"][i])[0]
            indexTwo = np.where(gameIds == similarityTests["id_game_two"][i])[0]
            indexThree = np.where(gameIds == similarityTests["id_game_three"][i])[0]

            if similarityTests["result"][i] == 4:

                continue

            elif similarityTests["result"][i] == 0 and pred[indexTest] == pred[indexOne]:

                rate += 1.0

            elif similarityTests["result"][i] == 1 and pred[indexTest] == pred[indexTwo]:

                rate += 1.0

            elif similarityTests["result"][i] == 2 and pred[indexTest] == pred[indexThree]:

                rate += 1.0

            nbTest += 1

        if nbTest < 1:
            print("WARNING: Aucun test valide pour noter les modèles.")
            return -1.0

        return rate / nbTest

    def getRandomParam(self):

        randBuffer = randint(self.confModels["nearestNeightboor"][0], self.confModels["nearestNeightboor"][1])
        neirNeight = int(randBuffer - (randBuffer % self.confModels["nearestNeightboor"][2]))
        randBuffer = randint(self.confModels["alpha"][0], self.confModels["alpha"][1])
        alpha = int(randBuffer - (randBuffer % self.confModels["alpha"][2]))
        randBuffer = randint(self.confModels["minGameByCat"][0], self.confModels["minGameByCat"][1])
        minGameByCat = int(randBuffer - (randBuffer % self.confModels["minGameByCat"][2]))

        return neirNeight, alpha, minGameByCat

    @staticmethod
    def isParamAlreadyExist(params, existModels):

        for i in range(len(existModels["near_neight"])):

            if existModels["near_neight"][i] == params[0] and \
                    existModels["alpha"][i] == params[1] and \
                    existModels["min_game_by_cat"][i] == params[2]:
                return True

        return False
