import logging
import time
import threading
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from app.database import Database
from app.email_sender import EmailSender


class EmailOperation:
	def __init__(self):
		self.db = Database()
		self.email_sender = EmailSender()
		self.lock = threading.Lock()
	
	def count_users(self):
		try:
		
			all_users = self.db.get_all_users()
			
			if not all_users:
				logging.error("EmailOpr == No data found in the database")
				return 0
			
			counts = {
				'three_months_count': {'nb': 0, 'date': ''},
				'six_months_count': {'nb': 0, 'date': ''},
				'more_six_months_count': {'nb': 0, 'date': ''},
				'less_three_months': {'nb': 0, 'date': ''},
				'less_six_months': {'nb': 0, 'date': ''}
			}
			
			for user in all_users:
				user_dict = {
					'last_name': user[1],
					'first_name': user[2],
					'email': user[3],
					'last_interview': user[4],
					'status_tree_months': user[5],
					'status_six_months': user[6],
					'status_more_six_months': user[7],
				}
				
				
				last_date = user_dict['last_interview']
				months = self.calculate_months(last_date)
				last_interview_months = months['interview_months']
				
				if last_interview_months == months['three_months_ago']:
					if user_dict['status_tree_months'] == 0:
						counts['three_months_count']['nb'] += 1
				elif last_interview_months == months['six_months_ago']:
					if user_dict['status_six_months'] == 0:
						counts['six_months_count']['nb'] += 1
				elif months['more_six_months']:
					if user_dict['status_more_six_months'] == 0:
						counts['more_six_months_count']['nb'] += 1
				elif months['less_three_months']:
					counts['less_three_months']['nb'] += 1
				elif months['less_six_months']:
					counts['less_six_months']['nb'] += 1
			
			counts['three_months_count']['date'] = self.convert_month_to_name(months['three_months_ago'])
			counts['six_months_count']['date'] = self.convert_month_to_name(months['six_months_ago'])
			counts['more_six_months_count']['date'] = self.convert_month_to_name(months['six_months_ago'])
			
			return counts
		except Exception as e:
			logging.error(f"Error_count_user: {e}")
			return 0
	
	def convert_month_to_name(self, month_str):
		month_names = {
			'01': 'Janvier', '02': 'Février', '03': 'Mars', '04': 'Avril',
			'05': 'Mai', '06': 'Juin', '07': 'Juillet', '08': 'Août',
			'09': 'Septembre', '10': 'Octobre', '11': 'Novembre', '12': 'Décembre'
		}
		month_number = month_str.split('/')[0]
		return month_names.get(month_number, "Mois inconnu")
	
	def calculate_months(self, last_interview):
		today = date.today()
		three_months_ago = today - relativedelta(months=3)
		six_months_ago = today - relativedelta(months=6)
		try:
			last_interview_date = datetime.strptime(last_interview, "%d/%m/%y").date()
		except ValueError as e:
			logging.error(f"Date format error: {e}")
			raise
		
		more_six_months = last_interview_date < six_months_ago
		less_six_months = six_months_ago <= last_interview_date < three_months_ago
		less_three_months = last_interview_date >= three_months_ago
		
		months = {
			'three_months_ago': three_months_ago.strftime("%m/%y"),
			'six_months_ago': six_months_ago.strftime("%m/%y"),
			'more_six_months': more_six_months,
			'less_six_months': less_six_months,
			'less_three_months': less_three_months,
			'interview_months': last_interview_date.strftime("%m/%y"),
		}
		
		return months
	
	def try_send_email(self):
		try:
			all_users = self.db.get_all_users()
			if not all_users:
				logging.error("EmailOpr == No data found in the database")
				return 0
			
			threads = []
			email_counter = 0
			
			for user in all_users:
				user_dict = {
					'last_name': user[1],
					'first_name': user[2],
					'email': user[3],
					'last_interview': user[4],
					'status_tree_months': user[5],
					'status_six_months': user[6],
					'status_more_six_months': user[7],
				}
				
				thread = threading.Thread(target=self.process_user_email, args=(user_dict,))
				thread.start()
				threads.append(thread)
				email_counter += 1
				
				if email_counter % 10 == 0:
					time.sleep(5)
			
			for thread in threads:
				thread.join()
			
			return True
		except Exception as e:
			logging.error(f"Error_try_send_email: {e}")
			return False
	
	def process_user_email(self, user_dict):
		try:
			# Create a new database connection in this thread
			db = Database()
			
			last_date = user_dict['last_interview']
			months = self.calculate_months(last_date)
			last_interview_months = months['interview_months']
			
			if last_interview_months == months['three_months_ago']:
				if user_dict['status_tree_months'] == 0:
					if self.email_sender.send_email_after_3_months(user_dict):
						with self.lock:
							db.update_status_email3(user_dict['email'])
			elif last_interview_months == months['six_months_ago']:
				if user_dict['status_six_months'] == 0:
					if self.email_sender.send_email_after_6_months(user_dict):
						with self.lock:
							db.update_status_email6(user_dict['email'])
			elif months['more_six_months']:
				if user_dict['status_more_six_months'] == 0:
					if self.email_sender.send_email_after_more_than_6_months(user_dict):
						with self.lock:
							db.update_status_email_plus_6(user_dict['email'])
		except Exception as e:
			logging.error(f"Error_process_user_email: {e}")
	


