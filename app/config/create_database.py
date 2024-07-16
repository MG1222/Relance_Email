# In create_database.py
import os
import sqlite3
import logging
import sys


class DatabaseInitializer:
	if getattr(sys, 'frozen', False):
		# Si l'application est exécutée en tant que .exe compilé
		application_path = os.path.dirname(sys.executable)
	else:
		# Si l'application est exécutée en mode développement (par exemple, via un IDE ou directement depuis le script Python)
		application_path = os.path.dirname(__file__)
	
	DB_PATH = os.path.join(application_path, 'bdd', 'db_relance_rh.db')
	@staticmethod
	def init_db():
		try:
			os.makedirs(os.path.dirname(DatabaseInitializer.DB_PATH), exist_ok=True)
			logging.info(f"Connecting to the database at path: {DatabaseInitializer.DB_PATH}")
			conn = sqlite3.connect(DatabaseInitializer.DB_PATH)
			cursor = conn.cursor()
			cursor.execute('''CREATE TABLE IF NOT EXISTS relance_rh
                              (id INTEGER PRIMARY KEY AUTOINCREMENT, last_name TEXT, first_name TEXT, email TEXT UNIQUE,
                              last_interview TEXT, email_3 BOOLEAN DEFAULT FALSE,
                              email_6 BOOLEAN DEFAULT FALSE, email_plus_6 BOOLEAN DEFAULT FALSE)''')
			conn.commit()
			conn.close()
			logging.info("Database initialized successfully.")
		except sqlite3.OperationalError as oe:
			logging.error(f"OperationalError occurred: {oe}")
			raise oe
		except Exception as e:
			logging.error(f"An unexpected error occurred: {e}")
			raise e
