from .dataFormater import cleanGameData
from .trainer import Trainer
from random import randint
from time import sleep
import numpy as np
import os


class ModelManager:

    def __init__(self, postgresDao, modelType, confModels, outputDir):

        self.postgresDao = postgresDao
        self.modelType = modelType
        self.confModels = confModels
        self.nearestNeightboor = confModels["defaultNearestNeightboor"]
        self.alpha = confModels["defaultAlpha"]
        self.minGameByCat = confModels["defaultMinGameByCat"]
        self.outputDir = outputDir
        self.chooseModels()

    def chooseModels(self):

        models = self.postgresDao.getModels(self.modelType)
        trainer = Trainer(self.modelType, self.nearestNeightboor, self.alpha, self.minGameByCat, self.outputDir,
                          self.postgresDao, True)

        print("INFO: {0} modèles de type {1}.".format(len(models["name"]), self.modelType))

        if len(models["name"]) < 1:

            print("INFO: Entrainement du modèle par défault...")
            dictData = self.postgresDao.getGameDataset()
            dataset = cleanGameData(dictData)
            trainer.run(dataset)
            model = trainer.loadModel("default")
            modelName = "default"

        elif len(models["name"]) > 1:

            bestModelName = "default"
            bestModelNote = models["note"][models["name"].index("default")]

            for i in range(0, len(models["name"])):

                if models["name"][i] == "default":
                    continue

                if models["note"][i] > bestModelNote and models["nb_test"][i] > 4:
                    bestModelNote = models["note"][i]
                    bestModelName = models["name"][i]

            model = trainer.loadModel(bestModelName)
            modelName = bestModelName

            print("INFO: Meilleur modèle: {}.".format(modelName))

        else:

            model = trainer.loadModel("default")
            modelName = "default"

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

            trainer = Trainer(self.modelType, newModel[0], newModel[1], newModel[2], self.outputDir,
                              self.postgresDao, False)
            trainer.run(dataset)
            sleep(1)

    def generateTestForModels(self, nbTestForModel):

        trainer = Trainer(self.modelType, self.nearestNeightboor, self.alpha, self.minGameByCat, self.outputDir,
                          self.postgresDao)

        dictData = self.postgresDao.getGameDataset()
        dataset = cleanGameData(dictData)

        for file in os.listdir(self.outputDir):

            if file != ".gitignore":

                modelName = file.replace(".joblib", "")
                idModel = self.postgresDao.getModelIdByName(modelName)

                model = trainer.loadModel(modelName)
                model, pred = trainer.clusterize(dataset, model)

                print(
                    "INFO: Génération de {} tests pour le modèle {} id {}.".format(nbTestForModel, modelName, idModel))

                for i in range(nbTestForModel):
                    self.createModelTest(dataset, pred, idModel)

    def createModelTest(self, dataset, pred, idModel):

        bufferIndexs = np.where(pred != -1)[0]
        testGameIndex = bufferIndexs[randint(0, len(bufferIndexs) - 1)]
        testGameId = int(dataset[0][testGameIndex])
        testCat = pred[testGameIndex]

        print("INFO: Modèle {} - Jeu référence {} - catégorie {} - taille de la catégorie {}."
              .format(idModel, testGameId, testCat, len(np.where(pred == testCat)[0])))

        if len(np.where(pred == testCat)[0]) < 2:
            print("ERROR: Taille de la catégorie {} trop faible pour le test.".format(testCat))
            return

        nearGameId = testGameId

        while nearGameId == testGameId:
            bufferIndexs = np.where(pred == testCat)[0]
            indexNearGame = bufferIndexs[randint(0, len(bufferIndexs) - 1)]
            nearGameId = int(dataset[0][indexNearGame])

        print("INFO: Modèle {} - Jeu proche {}.".format(idModel, nearGameId))

        bufferIndexs = np.where((pred != testCat) & (pred != -1))[0]

        if len(bufferIndexs) < 2:
            print("ERROR: Taille de la catégorie {} trop faible pour le test.".format(testCat))
            return

        indexGameOne = bufferIndexs[randint(0, len(bufferIndexs) - 1)]
        idGameOne = int(dataset[0][indexGameOne])
        catGameOne = pred[indexGameOne]

        print("INFO: Modèle {} - Jeu éloigné 1 {} - catégorie {}.".format(idModel, idGameOne, catGameOne))

        bufferIndexs = np.where((pred != testCat) & (pred != -1) & (pred != catGameOne))[0]

        if len(bufferIndexs) < 2:
            print("ERROR: Taille de la catégorie {} trop faible pour le test.".format(testCat))
            return

        indexGameTwo = bufferIndexs[randint(0, len(bufferIndexs) - 1)]
        idGameTwo = int(dataset[0][indexGameTwo])

        print("INFO: Modèle {} - Jeu éloigné 2 {} - catégorie {}.".format(idModel, idGameTwo, pred[indexGameTwo]))

        self.postgresDao.insertModelTest(idModel, testGameId, nearGameId, idGameOne, idGameTwo)

    def updateModelRates(self):

        modelIds = self.postgresDao.getModelIds(self.modelType)

        print("INFO: Mise à jour des notes des {} modèles existant.".format(len(modelIds)))

        for modelId in modelIds:

            rates = self.postgresDao.getModelRatesById(modelId)

            if len(rates) > 0:

                avg = np.average(np.array(rates))
                self.postgresDao.updateModelRecRate(modelId, avg, len(rates))
                print("INFO: Modèle {} - {} notes - moyenne {}.".format(modelId, len(rates), avg))

            else:

                print("INFO: Aucune note pour le modèle {}.".format(modelId))

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
