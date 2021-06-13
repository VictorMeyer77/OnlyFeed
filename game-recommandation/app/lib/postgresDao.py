from psycopg2 import pool
from datetime import datetime
import sys


class PostgresDao:

    def __init__(self, confPostgres):

        try:

            self.pool = pool.SimpleConnectionPool(1, 10, host=confPostgres["host"],
                                                  port=confPostgres["port"],
                                                  dbname=confPostgres["database"],
                                                  user=confPostgres["user"],
                                                  password=confPostgres["password"])

            print("INFO: Connection établie avec {}.".format(confPostgres["database"]))

        except Exception as e:

            print("ERROR: Impossible de se connecter à la base de données")
            print(e)
            sys.exit()

    def getGameDataset(self):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("""select vg.id,
                           vg.release_date,
                           vg.genres,
                           vg.price,
                           vg.currency,
                           vg.age,
                           vg.windows,
                           vg.mac,
                           vg.linux,
                           vg.publishers,
                           vg.developers,
                           ga.graphic,
                           ga.gameplay,
                           ga.lifetime,
                           ga.immersion,
                           ga.extern
                           from (select distinct id_game, date_maj, graphic, gameplay, lifetime,
                           immersion, extern from of_game_analysis order by date_maj desc) as ga
                           left join steam_video_games as vg ON ga.id_game = vg.id""")

            resultReq = cursor.fetchall()

            return self.extractDataset(resultReq)

        except Exception as e:

            print("ERROR getGameDataset: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def getModels(self, modelType):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("""select distinct model_name, note, nb_test, near_neight, alpha, min_game_by_cat, date_maj
                           from of_recommandation_model
                           where recommandation_type = %s
                           order by date_maj desc""", (modelType,))

            resultReq = cursor.fetchall()

            return self.extractModels(resultReq)

        except Exception as e:

            print("ERROR getModels: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def getModelIds(self, modelType):

        conn = None

        try:

            ids = []
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("""select distinct id from of_recommandation_model where recommandation_type = %s""",
                           (modelType,))

            for res in cursor.fetchall():
                ids.append(res[0])

            return ids

        except Exception as e:

            print("ERROR getModelIds: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def getModelRatesById(self, modelId):

        conn = None

        try:

            rates = []
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("""select r.result from of_model_test_result as r left join of_model_test as t on 
                           r.id_test = t.id where t.id_model = %s and r.result != 2""",
                           (modelId,))

            for res in cursor.fetchall():
                rates.append(res[0])

            return rates

        except Exception as e:

            print("ERROR getModelIds: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)


    def getOfUserId(self):

        conn = None

        try:

            ids = []
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("select id from of_user")
            resultReq = cursor.fetchall()

            for res in resultReq:
                ids.append(res[0])

            return ids

        except Exception as e:

            print("ERROR getOfUserId: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def getGameUserEvaluation(self):

        conn = None

        try:

            evals = {"of_user_id": [], "game_id": [], "rate": []}
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("select of_user_id, game_id, rate from of_game_user_evaluation")
            resultReq = cursor.fetchall()

            for res in resultReq:
                evals["of_user_id"].append(res[0])
                evals["game_id"].append(res[1])
                evals["rate"].append(res[2])

            return evals

        except Exception as e:

            print("ERROR getGameUserEvaluation: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def getModelIdByName(self, modelName):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("select id from of_recommandation_model where model_name = %s", (modelName,))
            resultReq = cursor.fetchall()

            if len(resultReq) < 1:
                print("WARNING: Aucun modèle enregistré sous le nom de {}.".format(modelName))
                return -1

            return resultReq[0][0]

        except Exception as e:

            print("ERROR gameModelIdByName: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def insertModel(self, modelName, recommandationType, nearNeight, alpha, minGameByCat):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            now = str(datetime.now())
            cursor.execute("INSERT INTO of_recommandation_model "
                           "(model_name, recommandation_type, note, nb_test, "
                           "near_neight, alpha, min_game_by_cat, date_maj) "
                           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                           (modelName, recommandationType, 0.5, 0, nearNeight, alpha, minGameByCat, now))

            conn.commit()

        except Exception as e:

            print("ERROR insertModel: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def insertGameRecommandation(self, gameId, modelId, ofUserId):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            now = str(datetime.now())
            cursor.execute("INSERT INTO of_game_recommandation "
                           "(of_user_id, game_id, model_id, date_create) "
                           "VALUES (%s, %s, %s, %s)",
                           (ofUserId, gameId, modelId, now))

            conn.commit()

        except Exception as e:

            print("ERROR insertGameRecommandation: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def insertModelTest(self, idModel, idGameTest, idGameNear, idGameOtherOne, idGameOtherTwo):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            now = str(datetime.now())
            cursor.execute("INSERT INTO of_model_test "
                           "(id_model, id_game_test, id_game_near, id_game_other_one, id_game_other_two, date_create) "
                           "VALUES (%s, %s, %s, %s, %s, %s)",
                           (idModel, idGameTest, idGameNear, idGameOtherOne, idGameOtherTwo, now))

            conn.commit()

        except Exception as e:

            print("ERROR insertModelTest: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def updateModelRecRate(self, idModel, rate, nbTest):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("UPDATE of_recommandation_model "
                           "SET note = %s, nb_test = %s "
                           "WHERE id = %s",
                           (idModel, rate, nbTest))

            conn.commit()

        except Exception as e:

            print("ERROR updateModelRecRate: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    @staticmethod
    def extractModels(sqlResponse):

        models = {"name": [],
                  "note": [],
                  "nb_test": [],
                  "near_neight": [],
                  "alpha": [],
                  "min_game_by_cat": [],
                  "date_maj": []}

        for response in sqlResponse:
            models["name"].append(response[0])
            models["note"].append(response[1])
            models["nb_test"].append(response[2])
            models["near_neight"].append(response[3])
            models["alpha"].append(response[4])
            models["min_game_by_cat"].append(response[5])
            models["date_maj"].append(response[6])

        return models

    @staticmethod
    def extractDataset(sqlResponse):

        dataset = {"id": [],
                   "release_date": [],
                   "genres": [],
                   "price": [],
                   "currency": [],
                   "age": [],
                   "windows": [],
                   "mac": [],
                   "linux": [],
                   "publishers": [],
                   "developers": [],
                   "graphic": [],
                   "gameplay": [],
                   "lifetime": [],
                   "immersion": [],
                   "extern": []}

        for response in sqlResponse:
            dataset["id"].append(response[0])
            dataset["release_date"].append(response[1])
            dataset["genres"].append(response[2])
            dataset["price"].append(response[3])
            dataset["currency"].append(response[4])
            dataset["age"].append(response[5])
            dataset["windows"].append(response[6])
            dataset["mac"].append(response[7])
            dataset["linux"].append(response[8])
            dataset["publishers"].append(response[9])
            dataset["developers"].append(response[10])
            dataset["graphic"].append(response[11])
            dataset["gameplay"].append(response[12])
            dataset["lifetime"].append(response[13])
            dataset["immersion"].append(response[14])
            dataset["extern"].append(response[15])

        return dataset
