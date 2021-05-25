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
                                                  password=confPostgres["password"],
                                                  sslmode="require")

            print("INFO: Connection établie avec {}.".format(confPostgres["database"]))

        except Exception as e:

            print("ERROR: Impossible de se connecter à la base de données")
            print(e)
            sys.exit()

    def getPgGameIds(self):

        conn = None

        try:

            ids = []
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("select id from steam_video_games")
            resultReq = cursor.fetchall()

            for gameId in resultReq:
                ids.append(gameId[0])

            return ids

        except Exception as e:

            print("ERROR getPgGameIds: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def getPgInvalidGameIds(self):

        conn = None

        try:

            ids = []
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("select id from steam_invalid_game_ids")
            resultReq = cursor.fetchall()

            for gameId in resultReq:
                ids.append(gameId[0])

            return ids

        except Exception as e:

            print("ERROR getPgInvalidGameIds: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def insertSteamGame(self, info):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO steam_video_games (id,"
                           "name,"
                           "age,"
                           "languages,"
                           "windows,"
                           "mac,"
                           "linux,"
                           "windows_requirements,"
                           "mac_requirements,"
                           "linux_requirements,"
                           "publishers,"
                           "developers,"
                           "price,"
                           "currency,"
                           "categories,"
                           "genres,"
                           "recommendations,"
                           "release_date)"
                           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", info)

            cursor.execute("INSERT INTO steam_game_reviews_flag (game_id, flag, date_maj) VALUES (%s, %s, %s)",
                           (info[0], "*", str(datetime.now())))

            conn.commit()
            print("INFO: {} inséré dans la base de données.".format(info[1]))

        except Exception as e:

            print("ERROR insertSteamGame: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def insertSteamInvalidGame(self, gameId):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO steam_invalid_game_ids (id) VALUES (%s)", (gameId,))
            conn.commit()
            print("INFO: {} Id invalide inséré dans la base de données.".format(str(gameId)))

        except Exception as e:

            print("ERROR insertSteamInvalidGame: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def getGameFlags(self):

        conn = None

        try:

            flags = {"id": [], "cursor": []}
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT game_id, flag FROM steam_game_reviews_flag ORDER BY date_maj")
            resultReq = cursor.fetchall()

            for res in resultReq:
                flags["id"].append(res[0])
                flags["cursor"].append(res[1])

            return flags

        except Exception as e:

            print("ERROR getGameFlags: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def insertGameReview(self, review):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO steam_game_reviews"
                           " (id, author_id, game_id, date_create, review)"
                           " VALUES (%s, %s, %s, %s, %s)", review)
            conn.commit()

        except Exception as e:

            print("ERROR insertGameReview: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def updateFlag(self, gameId, flag):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            now = str(datetime.now())
            cursor.execute("UPDATE steam_game_reviews_flag SET flag = %s, date_maj = %s WHERE game_id = %s",
                           (flag, now, gameId))

            conn.commit()

        except Exception as e:

            print("ERROR insertGameReview: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)
