from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import psycopg2
import datetime

POSTGRES = {
    'user': 'of_dck',
    'pw': 'gft78kP9!luY!',
    'db': 'onlyfeed',
    'host': 'onlyfeed.ddns.net',
    'port': '5432',
}

db = psycopg2.connect( host=POSTGRES['host'], user=POSTGRES['user'], password=POSTGRES['pw'], dbname=POSTGRES['db'])


class Get_Video_Game_Price(Action):

    def name(self) -> Text:
        return "Get_Video_Game_Price"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        video_game = tracker.get_slot("video_game")

        if(not video_game):
            dispatcher.utter_template("utter_not_found", tracker)
        else:
            video_game = video_game.lower()
            price = fetch_price(video_game)
            if(not price):
                dispatcher.utter_template("utter_not_found", tracker)
            else:
                price = price[0][0] / 100
                dispatcher.utter_template("utter_give_price", tracker, price=price, video_game=video_game)

        return []

class Get_Video_Game_Rate(Action):

    def name(self) -> Text:
        return "Get_Video_Game_Rate"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        video_game = tracker.get_slot("video_game")

        if(not video_game):
            dispatcher.utter_template("utter_not_found", tracker)
        else:
            video_game = video_game.lower()
            rate = fetch_rate(video_game)
            if(not rate):
                dispatcher.utter_template("utter_not_found", tracker)
            else:
                dispatcher.utter_template("utter_give_rate", tracker, graphic = rate[0][0], gameplay = rate[0][1], lifetime = rate[0][2], immersion = rate[0][3], extern = rate[0][4])

        return []

class Get_Recommandation(Action):

    def name(self) -> Text:
        return "Get_Recommandation"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_id = tracker.current_state()["sender_id"]
        video_game = fetch_recommandation(user_id)

        dispatcher.utter_template("utter_give_recommandation", tracker, video_game=video_game)

        return []


class Get_Latest_Game(Action):

    def name(self) -> Text:
        return "Get_Latest_Game"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        latest_game = get_latest_game()
        dispatcher.utter_template("utter_give_latest_game", tracker, latest_game = latest_game)

        return []

class Get_Requirements(Action):

    def name(self) -> Text:
        return "Get_Requirements"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        video_game = tracker.get_slot("video_game")
        
        if(not video_game):
            dispatcher.utter_template("utter_not_found", tracker)
        else:
            video_game = video_game.lower()
            requirements = get_requirements(video_game)
            if(not requirements[0][5]):
                dispatcher.utter_template("utter_not_found", tracker)
            else:
                if(requirements[0][0]):
                    mac_ok = "Oui"
                else:
                    mac_ok = "Non"
                if(requirements[0][1]):
                    linux_ok = "Oui"
                else:
                    linux_ok = "Non"
                if(requirements[0][2]):
                    windows_ok = "Oui"
                else:
                    windows_ok = "Non"
                dispatcher.utter_template("utter_give_requirements", tracker, linux_ok = linux_ok, mac_ok = mac_ok, windows_ok = windows_ok, mac_requirements = requirements[0][3], linux_requirements = requirements[0][4], windows_requirements = requirements[0][5])

        return []

class Get_Evaluation(Action):

    def name(self) -> Text:
        return "Get_Evaluation"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_id = tracker.current_state()["sender_id"]
        rate = tracker.latest_message['text']
        id_evaluated_game = fetch_id_game_recommandation(user_id)
        save_user_evaluation(id_evaluated_game, user_id, rate)

        dispatcher.utter_template("utter_happy", tracker)

        return []

class Get_Minimum_Age(Action):

    def name(self) -> Text:
        return "Get_Minimum_Age"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        video_game = tracker.get_slot("video_game")
        
        if(not video_game):
            dispatcher.utter_template("utter_not_found", tracker)
        else:
            video_game = video_game.lower()
            age = get_minimum_age(video_game)

            if(age[0][0] is None):
                dispatcher.utter_template("utter_not_found", tracker)
            else:
                dispatcher.utter_template("utter_give_minimum_age", tracker, age = age[0][0], video_game = video_game)

        return []

class Get_Latest_Review(Action):

    def name(self) -> Text:
        return "Get_Latest_Review"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        video_game = tracker.get_slot("video_game")
        
        if(not video_game):
            dispatcher.utter_template("utter_not_found", tracker)
        else:
            video_game = video_game.lower()
            latest_review = get_latest_review(video_game)

            if(not latest_review[0][0]):
                dispatcher.utter_template("utter_not_found", tracker)
            else:
                dispatcher.utter_template("utter_give_latest_review", tracker, latest_review = latest_review[0][0], video_game = video_game)

        return []

def fetch_price(video_game):
    cur = db.cursor()
    cur.execute("SELECT price FROM steam_video_games WHERE LOWER(name) LIKE LOWER('%" + video_game +"%')")
    result = cur.fetchall()
    return result

def fetch_recommandation(user_id):
    cur = db.cursor()
    cur.execute("SELECT name FROM steam_video_games WHERE id = (SELECT game_id FROM of_game_recommandation a WHERE of_user_id = "+ user_id + " AND a.game_id NOT IN (SELECT game_id FROM of_game_user_evaluation WHERE of_user_id = "+ user_id + ") ORDER BY date_create DESC LIMIT 1)")
    result = cur.fetchall()
    return result[0][0]

def fetch_id_game_recommandation(user_id):
    cur = db.cursor()
    cur.execute("SELECT game_id FROM of_game_recommandation a WHERE of_user_id = "+ user_id + " AND a.game_id NOT IN (SELECT game_id FROM of_game_user_evaluation WHERE of_user_id = "+ user_id + ") ORDER BY date_create DESC LIMIT 1")
    result = cur.fetchall()
    return result[0][0]

def save_user_evaluation(game_id, user_id, rate):
    date_create = datetime.datetime.now()
    cur = db.cursor()

    try:
        cur.execute("INSERT INTO of_game_user_evaluation(of_user_id, game_id, rate, date_create) VALUES(" + str(user_id) + "," + str(game_id) + "," + str(rate) + ", '" + str(date_create) + "')")
        db.commit()
    except Exception as e:
        print(e)

def fetch_rate(video_game):
    cur = db.cursor()
    cur.execute("SELECT graphic, gameplay, lifetime, immersion, extern FROM of_game_analysis WHERE id_game = (SELECT id FROM steam_video_games WHERE LOWER(name) LIKE LOWER('%" + video_game +"%') LIMIT 1) ORDER BY date_maj DESC LIMIT 1")
    result = cur.fetchall()
    return result

def get_latest_game():
    cur = db.cursor()
    cur.execute("SELECT name FROM steam_video_games WHERE id IN (SELECT DISTINCT(id_game) FROM of_game_analysis) order by release_date DESC LIMIT 1")
    result = cur.fetchall()
    return result[0][0]

def get_requirements(video_game):
    cur = db.cursor()
    cur.execute("SELECT mac, linux, windows, mac_requirements, linux_requirements, windows_requirements FROM steam_video_games WHERE LOWER(name) LIKE '%"+ video_game +"%'")
    result = cur.fetchall()
    return result

def get_minimum_age(video_game):
    cur = db.cursor()
    cur.execute("SELECT age FROM steam_video_games WHERE LOWER(name) LIKE '%"+ video_game +"%'")
    result = cur.fetchall()
    return result

def get_latest_review(video_game):
    cur = db.cursor()
    cur.execute("SELECT review FROM steam_game_reviews WHERE game_id = (SELECT id FROM steam_video_games WHERE LOWER(name) LIKE '%"+ video_game +"%' LIMIT 1) ORDER BY date_create LIMIT 1")
    result = cur.fetchall()
    return result

print(get_latest_review("skyrim"))