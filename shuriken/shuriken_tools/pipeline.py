import sqlite
import json
import os

def list_to_json(items: list):
	return json.dumps(items).encode('utf8')


def json_to_list(data) -> list:
	return json.loads(data).decode('utf8')

class DBConnection:
	def __init__(self, db_name: str):
		self.db_name = db_name

	def setup(self):
		"""Set up the SQLite3 database."""
		sqlite3.register_adapter(list, list_to_json)
		sqlite3.register_converter('JSON', json_to_list)
		self.path = os.path.dirname(os.path.abspath(__file__))
		self.conn = sqlite3.connect(path + '/' + self.db_name, detect_types=sqlite3.PARSE_DECLTYPES)
		self.cur = conn.cursor()
		
		return self.cur, self.conn

	def push(self)
		pass