import os
import sqlite3
import logging
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from app.config.create_database import DatabaseInitializer


class Database(DatabaseInitializer):
	def __init__(self):
		super().init_db()
		self.conn = sqlite3.connect(self.DB_PATH)
		self.cursor = self.conn.cursor()
	
	def insert_data(self, data):
		try:
			query = "INSERT INTO relance_rh (last_name, first_name, email, last_interview) VALUES (?, ?, ?, ?)"
			self.cursor.execute(query,
			                    (data['last_name'], data['first_name'], data['email'], data['last_interview']))
			self.conn.commit()
		except sqlite3.IntegrityError:
			logging.error(f"Duplicate data: {data}")
		except Exception as e:
			logging.error(f"An error occurred: {e}")
			raise e
	
	def get_all_users(self):
		try:
			query = "SELECT * FROM relance_rh"
			self.cursor.execute(query)
			return self.cursor.fetchall()
		except Exception as e:
			logging.error(f"An error occurred: {e}")
			raise e
	
	def get_email(self):
		try:
			query = "SELECT email FROM relance_rh"
			self.cursor.execute(query)
			return self.cursor.fetchall()
		except Exception as e:
			logging.error(f"An error occurred: {e}")
			raise e
		
	def get_user_by_email(self, email):
		try:
			query = "SELECT * FROM relance_rh WHERE email = ?"
			self.cursor.execute(query, (email,))
			return self.cursor.fetchone()
		except Exception as e:
			logging.error(f"An error occurred: {e}")
			raise e
		
	def close_connection(self):
		self.conn.close()
		logging.info("Connection closed successfully.")
		
	def reset_table(self):
		try:
			query = "DELETE FROM relance_rh"
			self.cursor.execute(query)
			query = "DELETE FROM sqlite_sequence WHERE name='relance_rh'"
			self.cursor.execute(query)
			self.conn.commit()
			logging.info("Table relance_rh has been reset.")
			
		except Exception as e:
			logging.error(f"An error occurred while resetting the table: {e}")
			raise e
			
		
		
	def update_interview_date_by_email(self, email, new_date):
		try:
			query = "UPDATE relance_rh SET last_interview = ? WHERE email = ?"
			self.cursor.execute(query, (new_date, email))
			self.conn.commit()
			return True
			
		except Exception as e:
			logging.error(f"An error occurred while updating interview date for email {email}: {e}")
			return False
		
	def get_user_by_id(self, user_id):
		try:
			query = "SELECT * FROM relance_rh WHERE id = ?"
			self.cursor.execute(query, (user_id,))
			return self.cursor.fetchone()
		except Exception as e:
			logging.error(f"An error occurred: {e}")
			raise e
		
	def update_status_email3(self, email):
		try:
			query = "UPDATE relance_rh SET email_3 = 1 WHERE email = ?"
			self.cursor.execute(query, (email,))
			self.conn.commit()
			return True
		except Exception as e:
			logging.error(f"An error occurred while updating email_3 status for email {email}: {e}")
			return False
		
	def update_status_email6(self, email):
		try:
			query = "UPDATE relance_rh SET email_6 = 1 WHERE email = ?"
			self.cursor.execute(query, (email,))
			self.conn.commit()
			return True
		except Exception as e:
			logging.error(f"An error occurred while updating email_6 status for email {email}: {e}")
			return False
		
	def update_status_more_than_6(self, email):
		try:
			query = "UPDATE relance_rh SET more_than_6 = 1 WHERE email = ?"
			self.cursor.execute(query, (email,))
			self.conn.commit()
			return True
		except Exception as e:
			logging.error(f"An error occurred while updating more_than_6 status for email {email}: {e}")
			return False
		
	def update_status_email_plus_6(self, email):
		try:
			query = "UPDATE relance_rh SET email_plus_6 = 1 WHERE email = ?"
			self.cursor.execute(query, (email,))
			self.conn.commit()
			return True
		except Exception as e:
			logging.error(f"An error occurred while updating email_more_6 status for email {email}: {e}")
			return False
	
	def get_users_to_email(self):
		try:
			today = date.today()
			three_months_ago = today - relativedelta(months=3)
			six_months_ago = today - relativedelta(months=6)
			
			# Fetch users who need to be emailed
			query = """
	           SELECT * FROM relance_rh
	           WHERE
	           (last_interview = ? AND email_3 = FALSE) OR
	           (last_interview = ? AND email_6 = FALSE) OR
	           (last_interview < ? AND email_plus_6 = FALSE)
	           """
			self.cursor.execute(query, (three_months_ago.strftime('%d/%m/%y'), six_months_ago.strftime('%d/%m/%y'),
			                            six_months_ago.strftime('%d/%m/%y')))
			return self.cursor.fetchall()
		except Exception as e:
			logging.error(f"get_users_to_email == Error: {e}")
			return []


if __name__ == "__main__":
	reset = Database()
	reset.reset_table()
