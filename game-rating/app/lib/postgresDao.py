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

    def getGameIds(self):

        conn = None

        try:

            ids = []
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM steam_video_games")
            resultReq = cursor.fetchall()

            for res in resultReq:
                ids.append(res[0])

            return ids

        except Exception as e:

            print("ERROR getGameIds: " + str(e))

        finally:

            if conn is not None:

                self.pool.putconn(conn)

    def getGameReviews(self, gameId):

        conn = None

        try:

            reviews = ""
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT review FROM steam_game_reviews WHERE game_id=%s", (gameId,))
            resultReq = cursor.fetchall()

            for res in resultReq:
                reviews += str(res[0])

            return reviews

        except Exception as e:

            print("ERROR getGameReviews: " + str(e))

        finally:

            if conn is not None:

                self.pool.putconn(conn)
