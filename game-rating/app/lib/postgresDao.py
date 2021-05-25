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

    def getGameIds(self):

        conn = None
        ids = []

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT distinct game_id FROM steam_game_reviews")
            resultReq = cursor.fetchall()

            for res in resultReq:
                ids.append(res[0])

        except Exception as e:

            print("ERROR getGameIds: " + str(e))

        finally:

            if conn is not None:

                self.pool.putconn(conn)

        return ids

    def getGameReviews(self, gameId):

        conn = None
        reviews = ""

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT review FROM steam_game_reviews WHERE game_id=%s", (gameId,))
            resultReq = cursor.fetchall()

            for res in resultReq:
                reviews += str(res[0])

        except Exception as e:

            print("ERROR getGameReviews: " + str(e))

        finally:

            if conn is not None:

                self.pool.putconn(conn)

        return reviews

    def getCriteraWords(self):

        conn = None
        criteraWords = {}

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT critera_id, word FROM of_words_by_critera")
            resultReq = cursor.fetchall()

            for res in resultReq:

                if res[0] not in criteraWords.keys():
                    criteraWords[res[0]] = []

                criteraWords[res[0]].append(res[1])

        except Exception as e:

            print("ERROR getCriteraWords: " + str(e))

        finally:

            if conn is not None:

                self.pool.putconn(conn)

        return criteraWords

    def insertGameRating(self, gameId, rates):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            now = str(datetime.now())
            cursor.execute("INSERT INTO of_game_analysis "
                           "(id_game, date_maj, graphic, gameplay, lifetime, immersion, extern) "
                           "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (gameId, now, *rates))

            conn.commit()

        except Exception as e:

            print("ERROR insertGameReview: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)