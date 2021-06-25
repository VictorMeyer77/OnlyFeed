from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

db = SQLAlchemy()
engine = create_engine('postgresql:///onlyfeed', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class Chatbot_User(Base):
	__tablename__ = 'of_user'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.Text)
	email = db.Column(db.Text)
	age = db.Column(db.Integer)

	def toJSON(self):       
		json = {
			"id":self.id,
			"username":self.username,
			"email":self.email,
			"age":self.age    
		}

		return json

class Chatbot_message_user(Base):
	__tablename__ = 'of_chatbot_message'

	id = db.Column(db.Integer, primary_key=True)
	id_user = db.Column(db.Text)
	type = db.Column(db.Text)
	date_send = db.Column(db.DateTime)
	content = db.Column(db.Text)

	def toJSON(self):       
		json = {
			"id":self.id,
			"id_user":self.id_user,
			"date_send":self.date_send,
			"content":self.content,
			"type":self.type    
		}

		return json