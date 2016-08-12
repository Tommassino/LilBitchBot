import logging
import json
import cymysql
import glob
import importlib
import os
from os.path import isfile
from importlib.machinery import SourceFileLoader
import bot
		
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('bot.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\n%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

PERSISTENCE_TABLE="user_persistence"

class Command(object):
	def __init__(self, regexp, callback, name=None, description=None):
		self.regexp=regexp
		self.callback=callback
		self.name=name
		self.description=description

class UserPersistence(object): 
	def __init__(self, database):
		self.database = database
		cursor = self.database.cursor()
		#cursor.execute("DROP TABLE {0}".format(PERSISTENCE_TABLE))
		cursor.execute("CREATE TABLE IF NOT EXISTS {0} (id BIGINT PRIMARY KEY, points FLOAT)".format(PERSISTENCE_TABLE))

	def add_user(self, userid, points):
		cursor = self.database.cursor()
		cursor.execute("INSERT INTO {0} (id, points) VALUES (%s, %s)".format(PERSISTENCE_TABLE), (userid,points,))
		self.database.commit()
		logger.debug(cursor._executed)
		
	def get_points(self, userid):
		cursor = self.database.cursor()
		cursor.execute("SELECT points FROM {0} WHERE id=%s".format(PERSISTENCE_TABLE), (userid,))
		logger.debug(cursor._executed)
		return cursor.fetchone()
		
	def add_points(self, userid, points):
		current_points = self.get_points(userid)
		logger.debug(current_points)
		if current_points:
			cursor = self.database.cursor()
			cursor.execute("UPDATE {0} SET points=points+%s WHERE id=%s".format(PERSISTENCE_TABLE), (points,userid,))
			self.database.commit()
			logger.debug(cursor._executed)
		else:
			self.add_user(userid,points) 
	
	def get_top(self, amount=3):
		cursor = self.database.cursor()
		cursor.execute("SELECT id,points FROM {0} ORDER BY points DESC LIMIT {1}".format(PERSISTENCE_TABLE,amount))
		logger.debug(cursor._executed)
		return cursor.fetchall()

class ClientConfig(object):
	def __init__(self, client, configPath):
		self.client=client
		self.modules = {} 
		self.config = {}      
		
		self.logger = logger
		self.handler = handler
		
		with open(configPath,'r') as fp:
			self.config=json.load(fp)
			
		database_config = self.config["database"]
		self.database = cymysql.connect(user=database_config["user"],passwd=database_config["password"],db=database_config["database"],host=database_config["host"],port=int(database_config["port"]))
		self.money = UserPersistence(self.database)
		
		logger.info('Loading modules...')
		path = os.path.join(bot.__path__[0], 'modules', '*.py')
		logger.debug(path)
		modules = glob.glob(path)
		for f in (m for m in modules if isfile(m)):
			dir,mod = f.rsplit('/',1)
			mod,py = mod.rsplit('.',1)
			logger.info('\t{0}'.format(mod))
			self.load_module(mod)

	def load_module(self, mod):
		path = os.path.join(bot.__path__[0], 'modules', '{0}.py')
		file = glob.glob(path.format(mod))
		if len(file)==0 or not isfile(file[0]):
			return None
		f = file[0]
		module = None
		module = SourceFileLoader(mod,f).load_module()
		init = module.Module(self)
		self.modules[mod]=init