import webbrowser
from tkinter import Frame, ttk, messagebox, StringVar, Toplevel, Scrollbar
import json
import logging
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from app.test_email_sender import TestEmailSender


class ParametersPage(Frame):
	def __init__(self, parent, controller, *args, **kwargs):
		super().__init__(parent, *args, **kwargs)
		self.emailOpr = TestEmailSender()
		self.controller = controller
		self.selected_option = StringVar()
		self.selected_test_option = StringVar()
		self.controller = controller
		
		self.grid_rowconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
		
		self.frame_smtp = ttk.Frame(self, borderwidth=2, relief="groove", padding=10)
		self.frame_smtp.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
		self.frame_test_email = ttk.Frame(self, borderwidth=2, relief="groove", padding=10)
		self.frame_test_email.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
		self.frame_email = ttk.Frame(self, borderwidth=2, relief="groove", padding=10)
		self.frame_email.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
		
		self.init_setting_smtp()
		self.init_test_email()
		self.init_setting_email()
		
		self.back_button_frame = ttk.Frame(self, padding=10)
		self.back_button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
		self.back_button_frame.grid_columnconfigure(0, weight=1)
		self.back_button_frame.grid_columnconfigure(1, weight=1)
		
		back_button = ttk.Button(self.back_button_frame, text="Retour",
		                         command=lambda: self.controller.show_frame("MainPage"))
		back_button.grid(row=0, column=1, pady=10, sticky="e")
		
		self.load_data_from_json()
	
	def init_setting_smtp(self):
		try:
			with open('./config/config_perso.json', 'r') as f:
				self.config = json.load(f)
		except FileNotFoundError:
			messagebox.showerror("Erreur", "Fichier de configuration non trouvé.")
			self.config = {}
		
		self.entries = {}
		
		for i, (param_name, default_value) in enumerate(self.config["email"].items()):
			label = ttk.Label(self.frame_smtp, text=param_name)
			label.grid(row=i, column=0, sticky="w", padx=10, pady=5)
			if param_name == "password":
				entry = ttk.Entry(self.frame_smtp, width=45, show="*")
				self.show_password_btn = ttk.Button(self.frame_smtp, text="Afficher",
				                                    command=lambda e=entry: self.toggle_password_visibility(e))
			else:
				entry = ttk.Entry(self.frame_smtp, width=45)
			entry.insert(0, str(default_value))
			entry.grid(row=i, column=1, padx=10, pady=5)
			self.entries[param_name] = entry
			if param_name == "password":
				self.show_password_btn.grid(row=i, column=2)
		
		save_button_frame1 = ttk.Button(self.frame_smtp, text="Enregistrer SMTP", command=self.save_settings_smtp)
		save_button_frame1.grid(row=len(self.config["email"]), column=0, columnspan=3, pady=10)
	
	def toggle_password_visibility(self, entry):
		if entry.cget("show") == "":
			entry.config(show="*")
			self.show_password_btn.config(text="Afficher")
		else:
			entry.config(show="")
			self.show_password_btn.config(text="Masquer")
	
	def init_test_email(self):
		try:
			with open('./config/config_perso.json', 'r') as f:
				self.config = json.load(f)
		except FileNotFoundError:
			messagebox.showerror("Erreur", "Fichier de configuration non trouvé.")
			self.config = {}
		
		self.entries = {}
		
		options = list(self.config.keys())[1:]
		if not options:
			messagebox.showerror("Erreur", "Aucune option trouvée dans la configuration.")
			return
		text = ttk.Label(self.frame_test_email, text="Test envoyer un email ")
		text.grid(row=0, column=0, padx=10, pady=5)
		self.selected_test_option.set(options[0])
		
		select_menu = ttk.OptionMenu(self.frame_test_email, self.selected_test_option, options[0], *options,
		                             command=self.update_test_email_label)
		select_menu.grid(row=3, column=0, padx=10, pady=5)
		
		text = ttk.Label(self.frame_test_email, text="Envoyer a  :")
		text.grid(row=1, column=0, padx=10, pady=5)
		
		self.test_email_entry = ttk.Entry(self.frame_test_email, width=35)
		self.test_email_entry.grid(row=2, column=0, padx=10, pady=5)
		
		# Extract and set the test email address from the config
		try:
			receiver_email_test = self.config["email_test"]["receiver_email_test"]
			self.test_email_entry.insert(0, receiver_email_test)
		except KeyError:
			messagebox.showerror("Erreur", "Adresse e-mail de test non trouvée dans la configuration.")
		
		send_test_email_button = ttk.Button(self.frame_test_email, text="Envoyer un email de test",
		                                    command=self.send_test_email)
		send_test_email_button.grid(row=4, column=0, padx=10, pady=5)
	
	def init_setting_email(self):
		options = list(self.config.keys())[1:]
		self.selected_option.set(options[0])
		
		select_menu = ttk.OptionMenu(self.frame_email, self.selected_option, options[0], *options,
		                             command=self.load_email_data)
		select_menu.grid(row=0, column=1, padx=10, pady=5)
		
		self.subject_label = ttk.Label(self.frame_email, text="Sujet de l'email")
		self.subject_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
		self.subject_entry = ttk.Entry(self.frame_email, width=50)
		self.subject_entry.grid(row=1, column=1, padx=10, pady=5)
		
		self.body_label = ttk.Label(self.frame_email, text="Corps de l'email")
		self.body_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
		
		self.body_text = ScrolledText(self.frame_email, wrap=tk.WORD, width=60, height=10)
		self.body_text.grid(row=2, column=1, padx=10, pady=5)
		
		save_button_email = ttk.Button(self.frame_email, text="Enregistrer Email", command=self.save_settings_email)
		save_button_email.grid(row=2, column=3, columnspan=2, pady=10)
	
	def load_data_from_json(self):
		try:
			with open('./config/config_perso.json', 'r') as f:
				self.config = json.load(f)
		except FileNotFoundError:
			messagebox.showerror("Erreur", "Fichier de configuration non trouvé.")
			self.config = {}
	
	def load_email_data(self, *args):
		selected_option = self.selected_option.get()
		
		if (selected_option in self.config) and (isinstance(self.config[selected_option], dict)):
			email_data = self.config[selected_option]
			self.subject_entry.delete(0, tk.END)
			self.subject_entry.insert(0, email_data.get("subject", ""))
			self.body_text.delete("1.0", tk.END)
			self.body_text.insert(tk.END, email_data.get("body", ""))
	
	def update_test_email_label(self, *args):
		selected_test_option = self.selected_test_option.get()
		self.test_email_label.config(text=f"Type d'email de test: {selected_test_option}")
	
	def save_settings_smtp(self):
		try:
			smtp_settings = {
				param_name: entry.get()
				for param_name, entry in self.entries.items()
			}
			smtp_settings["smtp_port"] = int(smtp_settings["smtp_port"])
			
			self.config["email"] = smtp_settings
			
			with open('./config/config_perso.json', 'w') as f:
				json.dump(self.config, f, indent=2)
			
			messagebox.showwarning("Enregistrés avec succès", "S'il vous plaît redémarrez l'application pour "
			                                                  "appliquer les modifications ")
			logging.info("Les paramètres SMTP ont été enregistrés avec succès")
			
		except ValueError:
			messagebox.showerror("Erreur", "Le port SMTP doit être un nombre entier.")
			logging.error("Erreur: Le port SMTP doit être un nombre entier.")
		except Exception as e:
			messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement des données: {e}")
			logging.error(f"Erreur lors de l'enregistrement des paramètres SMTP: {e}")
	
	def save_settings_email(self):
		try:
			selected_option = self.selected_option.get()
			email_template = {
				"subject": self.subject_entry.get(),
				"body": self.body_text.get("1.0", tk.END).strip()
			}
			
			self.config[selected_option] = email_template
			
			with open('./config/config_perso.json', 'w') as f:
				json.dump(self.config, f, indent=2)
			
			messagebox.showinfo("Enregistrement", "Les paramètres d'email ont été enregistrés avec succès")
			logging.info("Settings saved successfully")
		
		except Exception as e:
			messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement des données: {e}")
			logging.error(f"Setting email : Error {e}")
	
	def send_test_email(self):
		
		try:
			selected_test_option = self.selected_test_option.get()
			email_template = self.config[selected_test_option]
			send_email = self.emailOpr.send_test_email(email_template['subject'], email_template['body'])
			if send_email:
				messagebox.showinfo("Email envoyé", "Email de test envoyé avec succès")
			else:
				messagebox.showerror("Erreur", "Erreur lors de l'envoi de l'email de test")
		
		except Exception as e:
			messagebox.showerror("Erreur", f"Erreur lors de l'envoi de l'email de test: {e}")
			logging.error(f"Erreur lors de l'envoi de l'email de test: {e}")
