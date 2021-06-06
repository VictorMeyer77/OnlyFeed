from psycopg2 import pool
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
            cursor.execute("""select distinct model_name, note, nb_test, near_neight, alpha, nb_game_by_cat, date_maj
                           from of_game_recommandation_model
                           where recommandation_type = %s
                           order by date_maj desc""", (modelType,))

            resultReq = cursor.fetchall()

            return self.extractModels(resultReq)

        except Exception as e:

            print("ERROR getModels: " + str(e))

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
                  "nb_game_by_cat": [],
                  "date_maj": []}

        for response in sqlResponse:
            models["name"].append(response[0])
            models["note"].append(response[1])
            models["nb_test"].append(response[2])
            models["near_neight"].append(response[3])
            models["alpha"].append(response[4])
            models["nb_game_by_cat"].append(response[5])
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