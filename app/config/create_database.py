import os
import sqlite3
import logging
import sys


class DatabaseInitializer:
	if getattr(sys, 'frozen', False):
		# if .exe file
		application_path = os.path.dirname(sys.executable)
	else:
		# local
		application_path = os.path.dirname(__file__)
	
	DB_PATH = os.path.join(application_path, 'bdd', 'db_relance_rh.db')
	is_connected = False
	@staticmethod
	def init_db():
		if not DatabaseInitializer.is_connected:
			try:
				os.makedirs(os.path.dirname(DatabaseInitializer.DB_PATH), exist_ok=True)
				logging.info(f"Connecting to the database at path: {DatabaseInitializer.DB_PATH}")
				conn = sqlite3.connect(DatabaseInitializer.DB_PATH)

				cursor = conn.cursor()
				cursor.execute('''CREATE TABLE IF NOT EXISTS relance_rh
											  ( id INTEGER PRIMARY KEY AUTOINCREMENT, last_name TEXT, first_name TEXT, email TEXT UNIQUE,
											  last_interview TEXT, dont_email BOOLEAN DEFAULT FALSE, email_3 BOOLEAN DEFAULT FALSE,
											  email_6 BOOLEAN DEFAULT FALSE, email_12 BOOLEAN DEFAULT FALSE)''')
				cursor.execute('''CREATE TABLE IF NOT EXISTS last_path
				                              (id INTEGER PRIMARY KEY AUTOINCREMENT, last_path TEXT)''')
				conn.commit()
				cursor.close()
				DatabaseInitializer.is_connected = True
			except sqlite3.OperationalError as oe:
				logging.error(f"DatabaseInitializer = OperationalError occurred: {oe}")
				raise oe
			except Exception as e:
				logging.error(f"DatabaseInitializer = An unexpected error occurred: {e}")
				raise e


