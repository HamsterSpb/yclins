import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	#POSTGRES_USER = os.environ.get("POSTGRES_USER") // ladogalake
	#POSTGRES_PW = os.environ.get("POSTGRES_PW") //sadj34-Fzjh2dluz90
	#POSTGRES_URL = "rc1a-r5hhf0dowy61i1fz.mdb.yandexcloud.net"
	#POSTGRES_DB = "yclins"
	#SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}:{port}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB, port=6432)
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
