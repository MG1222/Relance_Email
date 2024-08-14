import logging
import time
import threading
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from app import excel_operation
from app.database import Database
from app.email_sender import EmailSender
from app.excel_operation import ExcelOperation


class EmailOperation:
    """
    This class is responsible for processing the emails.
    It's responsible for counting the users and sending the emails.
    it's little a bit complex not so clean , so need to refactor.
    """
    def __init__(self):
        self.db = Database()
        self.excel_opr = ExcelOperation()
        self.lock = threading.Lock()

    def count_users(self):
        """
        This method counts the users.
        We select the users who don't have flag to send email,
        we compare the last interview date with the current date.
        """

        try:
            all_users = self.db.get_users_dont_send_false()
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
                    'id': user[0],
                    'last_name': user[1],
                    'first_name': user[2],
                    'email': user[3],
                    'last_interview': user[4],
                    'dont_email': user[5],
                    'status_three_months': user[6],
                    'status_six_months': user[7],
                    'status_twelve_months': user[8],
                    'email_3': False,
                    'email_6': False,
                    'email_12': False,
                }
                self.excel_opr.clean_email_format(user_dict['email'], f"{user_dict['last_name']} {user_dict['first_name']}")

                last_date = user_dict['last_interview']
                months = self.calculate_months(last_date)
                last_interview_month = months['interview_month']

                if last_interview_month == months['three_months_ago'] and user_dict['status_three_months'] == 0:
                    counts['three_months_count']['nb'] += 1
                    counts['send_email'] += 1
                    user_dict['email_3'] = True
                    counts['users'].append(user_dict)

                elif last_interview_month == months['six_months_ago'] and user_dict['status_six_months'] == 0:
                    counts['six_months_count']['nb'] += 1
                    counts['send_email'] += 1
                    user_dict['email_6'] = True
                    counts['users'].append(user_dict)

                elif ((last_interview_month == months['twelve_months_ago'] or months['more_than_twelve_months']) and
                      user_dict['status_twelve_months'] == 0):
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
        """
        This method calculates the months between the last interview date and the current date.
        Because we need to know if the user has been interviewed in the last 3, 6 or 12 months.
        """
        today = date.today()
        three_months_ago = today - relativedelta(months=3)
        six_months_ago = today - relativedelta(months=6)
        twelve_months_ago = today - relativedelta(months=12)

        try:
            last_interview_date = datetime.strptime(last_interview, "%d/%m/%y").date()
        except ValueError as e:
            logging.error(f"EmailOpr = Date format error: {e}")
            raise

        months_between_6_and_3 = []
        current = six_months_ago + relativedelta(months=1)
        while current < three_months_ago:
            months_between_6_and_3.append(current.strftime("%m/%y"))
            current += relativedelta(months=1)

        months_less_than_3 = []
        current = three_months_ago + relativedelta(months=1)
        while current < today:
            months_less_than_3.append(current.strftime("%m/%y"))
            current += relativedelta(months=1)

        months_between_12_and_6 = []
        current = twelve_months_ago + relativedelta(months=1)
        while current < six_months_ago:
            months_between_12_and_6.append(current.strftime("%m/%y"))
            current += relativedelta(months=1)

        current = twelve_months_ago + relativedelta(months=1)
        months_more_than_12 = last_interview_date < current

        same_month = last_interview_date.strftime("%m/%y") == today.strftime("%m/%y")

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
        """
        This method tries to send the email to the users
        """
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
        """
        This method sends the email to the user.
        """
        global is_send
        try:
            email_sender = EmailSender()
            if user_dict['email_3']:
                is_send = email_sender.send_email_after_3_months(user_dict)
                self.db.update_status_email_3(user_dict['email'])
            elif user_dict['email_6']:
                is_send = email_sender.send_email_after_6_months(user_dict)
                self.db.update_status_email_6(user_dict['email'])
            elif user_dict['email_12']:
                is_send = email_sender.send_email_after_12_months(user_dict)
                self.db.update_status_email_12(user_dict['email'])
            if is_send:
                return True
            return False
        except Exception as e:
            logging.error(f"EmailOpr = Error_process_user_email: {e}")
            return False