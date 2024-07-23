import logging

import re
from tkinter import messagebox, BooleanVar
import openpyxl

from app.database import Database
from datetime import datetime
import re


class ExcelOperation:
    def __init__(self):
        self.folder = BooleanVar()
        self.file = BooleanVar()
        self.db = Database()
        self.error_messages = set()
    
    def verify_format_file_excel(self, file_path):
        try:
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active
            repartoire = sheet['A1'].value
            if repartoire != "REPARTOIRE":
                self.error_messages.add(f"Email manquant ou format incorrect: {file_path}")
                return False
            return True
        except Exception as e:
            self.error_messages.add(f"Erreur lors de la vérification du format du fichier.")
            logging.error(f"Error verifying file format: {file_path}. Error: {e}")
            return False
    
    def process_excel_file(self, file_path):
        if self.verify_format_file_excel(file_path):
            info_from_excel = self.extract_information_from_excel(file_path)
            if info_from_excel:
                return self.save_extracted_data(info_from_excel)
            else:
                self.error_messages.add(f"Erreur lors de l'extraction des informations du fichier: {file_path}, "
                                        f"verifiez le format des dates.")
                return False
        return False
    
    def extract_information_from_excel(self, file_path):
        try:
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active
            header_names = ['NOM', 'PRENOM', 'EMAIL', 'DERNIER ENTRETIEN']
            header_indices = {}
            
            for col_idx, cell in enumerate(sheet[1], start=1):
                if cell.value in header_names:
                    header_indices[cell.value] = col_idx - 1
            
            if len(header_indices) != len(header_names):
                self.error_messages.add(f"Le fichier ne contient pas tous les en-têtes nécessaires: {file_path}")
                logging.error(f"Missing headers in the file: {file_path}")
                raise ValueError("Not all expected headers found.")
            
            extracted_data = []
            invalid_date_found = False
            
            for row in sheet.iter_rows(min_row=2, values_only=True):
                last_name = row[header_indices['NOM']]
                first_name = row[header_indices['PRENOM']]
                email = row[header_indices['EMAIL']]
                last_interview_raw = row[header_indices['DERNIER ENTRETIEN']]
                last_interview = self.verify_format_date(last_interview_raw, f"{last_name} {first_name}", file_path)
                if last_interview is False:
                    continue
                
                if email is None:
                    logging.error(f"Email missing in row: {row} of file: {file_path}")
                    continue
                
                extracted_data.append({
                    'last_name': last_name,
                    'first_name': first_name,
                    'email': email,
                    'last_interview': last_interview
                })
            

            
            return extracted_data
        except Exception as e:
            self.error_messages.add(
                f"Problème lors de l'extraction des informations du fichier: {file_path}. Erreur: {e}")
            logging.error(f"Error extracting information from file: {file_path}. Error: {e}")
            return None
    
    def save_extracted_data(self, information):
        success = False
        duplicates = []
        self.error_messages.clear()
        for info in information:
            try:
                data = {
                    'last_name': info['last_name'],
                    'first_name': info['first_name'],
                    'email': info['email'],
                    'last_interview': info['last_interview'],
                }
                if not self.verify_duplicate(data['email']):
                    self.db.insert_data(data)
                    success = True
                else:
                    duplicates.append(data['email'])
            except Exception as e:
                self.error_messages.add(f"Échec de l'enregistrement des données.")
                logging.error(f"Failed to save data: {info}. Error: {e}")
        if duplicates:
            messagebox.showwarning("Avertissement",
                                   f"Des doublons ont été trouvés pour les adresses suivantes : {', '.join(duplicates)}. Ces entrées seront ignorées.")
        
        return success
    
    def verify_duplicate(self, email):
        data_bdd = self.db.get_user_by_email(email)
        if data_bdd:
            return True
        return False
    
    def verify_format_date(self, date, name, file_path):
        if isinstance(date, datetime):
            return date.strftime('%d/%m/%y')
        if isinstance(date, str):
            match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', date)
            if match:
                day, month, year = match.groups()
                if len(year) == 2 or len(year) == 4:  # Accepting only 2 or 4 digit years
                    corrected_date = f'{day}/{month}/{year}'
                    return corrected_date
                else:
                    logging.error(f"Invalid year format in date: {date} for {name}. Skipping user.")
                    messagebox.showwarning("Avertissement",
										   f"Format de date incorrect pour {name} dans {file_path}. il sera ignoré.")
                    return False  # Indicates an invalid date format
        logging.error(f"Invalid date format for {name}. Skipping user.")
        return False
        
    


