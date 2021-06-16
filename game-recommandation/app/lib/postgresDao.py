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
                           from (select * from of_game_analysis as r inner join (select id_game as i, max(date_maj) as d
                           from of_game_analysis group by id_game) as t on t.i = r.id_game and t.d = r.date_maj) as ga
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
            cursor.execute("""select model_name, near_neight, alpha, min_game_by_cat
                           from of_recommandation_model
                           where recommandation_type = %s""", (modelType,))

            resultReq = cursor.fetchall()

            return self.extractModels(resultReq)

        except Exception as e:

            print("ERROR getModels: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def getGameTestSimilarityResult(self):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("""select t.id_game_test, t.id_game_one, t.id_game_two, t.id_game_three, r.result 
                           from of_similarity_test_result as r
                           left join of_test_game_similarity as t on 
                           r.id_test = t.id""")

            return self.extractSimilarityTestResult(cursor.fetchall())

        except Exception as e:

            print("ERROR getGameTestSimilarityResult: " + str(e))

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

    def insertModel(self, modelName, recommandationType, nearNeight, alpha, minGameByCat):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            now = str(datetime.now())
            cursor.execute("INSERT INTO of_recommandation_model "
                           "(model_name, recommandation_type, "
                           "near_neight, alpha, min_game_by_cat, date_maj) "
                           "VALUES (%s, %s, %s, %s, %s, %s)",
                           (modelName, recommandationType, nearNeight, alpha, minGameByCat, now))

            conn.commit()

        except Exception as e:

            print("ERROR insertModel: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def insertGameRecommandation(self, gameId, ofUserId):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            now = str(datetime.now())
            cursor.execute("INSERT INTO of_game_recommandation "
                           "(of_user_id, game_id, date_create) "
                           "VALUES (%s, %s, %s)",
                           (ofUserId, gameId, now))

            conn.commit()

        except Exception as e:

            print("ERROR insertGameRecommandation: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def insertGameTestSimilarity(self, idGameTest, idGameOne, idGameTwo, idGameThree):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            now = str(datetime.now())
            cursor.execute("INSERT INTO of_test_game_similarity "
                           "(id_game_test, id_game_one, id_game_two, id_game_three, date_create) "
                           "VALUES (%s, %s, %s, %s, %s)",
                           (idGameTest, idGameOne, idGameTwo, idGameThree, now))

            conn.commit()

        except Exception as e:

            print("ERROR insertGameTestSimilarity: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def deleteModel(self, modelName):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("""DELETE FROM of_recommandation_model 
                           WHERE model_name = %s""", (modelName,))

            conn.commit()

        except Exception as e:

            print("ERROR deleteModel: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    @staticmethod
    def extractModels(sqlResponse):

        models = {"name": [],
                  "near_neight": [],
                  "alpha": [],
                  "min_game_by_cat": []}

        for response in sqlResponse:
            models["name"].append(response[0])
            models["near_neight"].append(response[1])
            models["alpha"].append(response[2])
            models["min_game_by_cat"].append(response[3])

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

    @staticmethod
    def extractSimilarityTestResult(sqlResponse):

        result = {"id_game_test": [],
                  "id_game_one": [],
                  "id_game_two": [],
                  "id_game_three": [],
                  "result": []}

        for response in sqlResponse:
            result["id_game_test"].append(response[0])
            result["id_game_one"].append(response[1])
            result["id_game_two"].append(response[2])
            result["id_game_three"].append(response[3])
            result["result"].append(response[4])

        return result
