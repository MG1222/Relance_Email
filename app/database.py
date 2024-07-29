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

    def insert_path(self, last_path):
        try:
            query = "INSERT INTO last_path (last_path) VALUES (?)"
            self.cursor.execute(query, (last_path,))
            self.conn.commit()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise e

    def get_last_path(self):
        try:
            query = "SELECT last_path FROM last_path ORDER BY id DESC LIMIT 1"
            self.cursor.execute(query)
            return self.cursor.fetchone()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise e

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

    def get_users_dont_send_false(self):
        query = "SELECT * FROM relance_rh WHERE dont_email = FALSE"
        try:
            self.cursor.execute(query)
            users = self.cursor.fetchall()
            return users
        except Exception as e:
            logging.error(f"Database = Error fetching users with dont_send = False: {e}")
            return []


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

    def update_status_email_3(self, email):
        try:
            query = "UPDATE relance_rh SET email_3 = 1 WHERE email = ?"
            self.cursor.execute(query, (email,))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"An error occurred while updating email_3 status for email {email}: {e}")
            return False

    def update_status_email_6(self, email):
        try:
            query = "UPDATE relance_rh SET email_6 = 1 WHERE email = ?"
            self.cursor.execute(query, (email,))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"An error occurred while updating email_6 status for email {email}: {e}")
            return False

    def update_status_email_12(self, email):
        try:
            query = "UPDATE relance_rh SET email_12 = 1 WHERE email = ?"
            self.cursor.execute(query, (email,))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"An error occurred while updating email_12 status for email {email}: {e}")
            return False


    def get_total_email_send(self):
        try:
            query = """
            SELECT
                SUM(CASE WHEN email_3 = 1 THEN 1 ELSE 0 END) AS email_3_count,
                SUM(CASE WHEN email_6 = 1 THEN 1 ELSE 0 END) AS email_6_count,
                SUM(CASE WHEN email_12 = 1 THEN 1 ELSE 0 END) AS email_12_count
            FROM relance_rh
            """
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            total = sum(result)
            return total
        except Exception as e:
            logging.error(f"An error occurred while fetching total email send: {e}")
            return 0

    def update_user(self, user_id, column_name, new_value):
        try:
            query = f"UPDATE relance_rh SET {column_name} = ? WHERE id = ?"
            self.cursor.execute(query, (new_value, user_id))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"An error occurred while updating user {user_id}: {e}")
            return False

    def get_users_by_name(self, name):
        try:
            query = "SELECT * FROM relance_rh WHERE last_name LIKE ?"
            self.cursor.execute(query, (name + '%',))
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"An error occurred while fetching users by name: {e}")
            raise e

    def get_users_by_email(self, email):
        try:
            query = "SELECT * FROM relance_rh WHERE email LIKE ?"
            self.cursor.execute(query, (email + '%',))
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"An error occurred while fetching users by email: {e}")
            raise e

if __name__ == "__main__":
    reset = Database()
    reset.reset_table()
