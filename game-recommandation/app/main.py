from lib.postgresDao import PostgresDao
from lib.recByEval import RecByEval
from lib.modelManager import ModelManager
import json
import sys

if __name__ == "__main__":

    conf = None

    try:

        file = open("../conf/configuration.json", "r")
        conf = json.load(file)

    except Exception as e:

        print("ERROR: " + str(e))
        sys.exit()

    postgresDao = PostgresDao(conf["postgres"])
    modelManager = ModelManager(postgresDao,
                                0,
                                conf["modelParams"],
                                conf["modelsDir"])

    if sys.argv[1] == "genrec":

        if len(sys.argv) < 3:

            print("ERROR: genrec prend un argument: le nombre de recommandations par user.")

        else:

            rec = RecByEval(postgresDao, modelManager)
            rec.run(int(sys.argv[2]))

    elif sys.argv[1] == "genmod":

        if len(sys.argv) < 4:

            print("ERROR: genmod prend deux argument: "
                  "le nombre de nouveaux modèles à créer et le nombre de test à générer.")

        else:

            modelManager.trainNewModels(int(sys.argv[2]))
            modelManager.generateGameTestSimilarity(int(sys.argv[3]))

    else:

        print("ERROR: Spécifier une commande: genrec ou genmod.")