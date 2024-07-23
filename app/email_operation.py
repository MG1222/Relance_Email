import logging
import time
import threading
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from app.database import Database
from app.email_sender import EmailSender


class EmailOperation:
    def __init__(self):

        self.db = Database()
        self.lock = threading.Lock()

    def count_users(self):
        try:
            all_users = self.db.get_all_users()
            if not all_users:
                logging.error("EmailOpr = No data found in the database")
                return 0

            counts = {
                'three_months_count': {'nb': 0, 'date': ''},
                'six_months_count': {'nb': 0, 'date': ''},
                'twelve_months_count': {'nb': 0, 'date': ''},
                'less_three_months': {'nb': 0, 'date': ''},
                'less_six_months': {'nb': 0, 'date': ''},
                'less_twelve_months': {'nb': 0, 'date': ''},
                'send_email': 0,
                'dont_send_email': 0,
                'users': []
            }

            for user in all_users:
                user_dict = {
                    'last_name': user[1],
                    'first_name': user[2],
                    'email': user[3],
                    'last_interview': user[4],
                    'status_three_months': user[5],
                    'status_six_months': user[6],
                    'status_twelve_months': user[7],
                    'email_3': False,
                    'email_6': False,
                    'email_12': False,

                }


                last_date = user_dict['last_interview']
                months = self.calculate_months(last_date)

                last_interview_month = months['interview_month']

                if last_interview_month == months['three_months_ago']:
                    if user_dict['status_three_months'] == 0:
                        counts['three_months_count']['nb'] += 1
                        counts['send_email'] += 1
                        user_dict['email_3'] = True
                        counts['users'].append(user_dict)

                elif last_interview_month == months['six_months_ago']:
                    if user_dict['status_six_months'] == 0:
                        counts['six_months_count']['nb'] += 1
                        counts['send_email'] += 1
                        user_dict['email_6'] = True
                        counts['users'].append(user_dict)

                elif last_interview_month == months['twelve_months_ago'] or months['more_than_twelve_months']:
                    if user_dict['status_twelve_months'] == 0:
                        counts['twelve_months_count']['nb'] += 1
                        counts['send_email'] += 1
                        user_dict['email_12'] = True
                        counts['users'].append(user_dict)

                elif last_interview_month in months['less_three_months'] or months['same_month']:
                    counts['less_three_months']['nb'] += 1
                    counts['dont_send_email'] += 1
                elif last_interview_month in months['less_six_months']:
                    counts['less_six_months']['nb'] += 1
                    counts['dont_send_email'] += 1
                elif last_interview_month in months['less_twelve_months']:
                    counts['less_twelve_months']['nb'] += 1
                    counts['dont_send_email'] += 1


            counts['three_months_count']['date'] = self.convert_month_to_name(months['three_months_ago'])
            counts['six_months_count']['date'] = self.convert_month_to_name(months['six_months_ago'])
            counts['twelve_months_count']['date'] = self.convert_month_to_name(months['twelve_months_ago'])

            return counts
        except Exception as e:
            logging.error(f"EmailOpr = Error_count_user: {e}")
            return 0

    def convert_month_to_name(self, month_str):
        month_names = {
            '01': 'Janvier', '02': 'Février', '03': 'Mars', '04': 'Avril',
            '05': 'Mai', '06': 'Juin', '07': 'Juillet', '08': 'Août',
            '09': 'Septembre', '10': 'Octobre', '11': 'Novembre', '12': 'Décembre'
        }
        parts = month_str.split('/')
        month_number = parts[0]
        year = parts[1] if len(parts) > 1 else "Année inconnue"
        month_name = month_names.get(month_number, "Mois inconnu")
        return f"{month_name} {year}"

    def calculate_months(self, last_interview):
        today = date.today()
        three_months_ago = today - relativedelta(months=3)
        six_months_ago = today - relativedelta(months=6)
        twelve_months_ago = today - relativedelta(months=12)

        # Parse the last interview date
        try:
            last_interview_date = datetime.strptime(last_interview, "%d/%m/%y").date()
        except ValueError as e:
            logging.error(f"EmailOpr = Date format error: {e}")
            raise

        # Calculate months between 6 and 3 months ago, excluding exactly 3 months ago
        months_between_6_and_3 = []
        current = six_months_ago + relativedelta(months=1)  # Start from the month after 6 months ago
        while current < three_months_ago:
            months_between_6_and_3.append(current.strftime("%m/%y"))
            current += relativedelta(months=1)

        # Calculate months less than 3 months ago, excluding the current month
        months_less_than_3 = []
        current = three_months_ago + relativedelta(months=1)  # Start from the month after 3 months ago
        while current < today:
            months_less_than_3.append(current.strftime("%m/%y"))
            current += relativedelta(months=1)

        # Calculate months between 12 and 6 months ago, excluding exactly 6 months ago
        months_between_12_and_6 = []
        current = twelve_months_ago + relativedelta(months=1)  # Start from the month after 12 months ago
        while current < six_months_ago:
            months_between_12_and_6.append(current.strftime("%m/%y"))
            current += relativedelta(months=1)

       # Calulate if last interview is more than 12 months ago
        current = twelve_months_ago + relativedelta(months=1)  # Start from the month after 12 months ago
        if last_interview_date < current:
            months_more_than_12 = True
        else:
            months_more_than_12 = False

        # Calculate if the last interview is the same month as today
        if last_interview_date.strftime("%m/%y") == today.strftime("%m/%y"):
            same_month = True
        else:
            same_month = False

        months = {
            'three_months_ago': three_months_ago.strftime("%m/%y"),
            'six_months_ago': six_months_ago.strftime("%m/%y"),
            'twelve_months_ago': twelve_months_ago.strftime("%m/%y"),
            'less_six_months': months_between_6_and_3,
            'less_three_months': months_less_than_3,
            'less_twelve_months': months_between_12_and_6,
            'interview_month': last_interview_date.strftime("%m/%y"),
            'more_than_twelve_months': months_more_than_12,
            'same_month': same_month
        }

        return months

    def try_send_email(self, progress_callback):
        try:
            all_users = self.count_users()
            users = all_users['users']

            if not users:
                logging.error("EmailOpr == No data found in the database")
                return 0

            total_emails = len(users)
            email_counter = 0

            for user in users:
                if self.send_email_to_user(user):
                    email_counter += 1
                    progress_callback(email_counter, total_emails)
                time.sleep(0.1)

            return True
        except Exception as e:
            logging.error(f"EmailOpr_try_send_email = Error_try_send_email: {e}")
            return False

    def send_email_to_user(self, user_dict):
        try:
            email_sender = EmailSender()
            if user_dict['email_3']:
                email_sender.send_email_after_3_months(user_dict)
                self.db.update_status_email_3(user_dict['email'])
            elif user_dict['email_6']:
                email_sender.send_email_after_6_months(user_dict)
                self.db.update_status_email_6(user_dict['email'])
            elif user_dict['email_12']:
                email_sender.send_email_after_12_months(user_dict)
                self.db.update_status_email_12(user_dict['email'])
            return True
        except Exception as e:
            logging.error(f"EmailOpr = Error_process_user_email: {e}")
            return False
