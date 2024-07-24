from tkinter import Frame, ttk, messagebox, StringVar, Toplevel, Scrollbar
import json
import logging
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from app.test_email_sender import TestEmailSender


class ParametersPage(Frame):
	def __init__(self, parent, controller, *args, **kwargs):
		super().__init__(parent, *args, **kwargs)


		self.controller = controller
		self.selected_option = StringVar()
		self.selected_test_option = StringVar()
		self.controller = controller
	
		self.smtp_config = {}
		self.test_email_config = {}
		self.email_templates = {}
		self.test_email_var = tk.StringVar()
		
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
	
	def load_config(self):
		"""Charge la configuration depuis le fichier JSON."""
		try:
			with open('./config/config_perso.json', 'r') as f:
				self.config = json.load(f)
	
		except FileNotFoundError:
			logging.error("Load config error: File not found.")
		except json.JSONDecodeError:
			logging.error("Load config error: JSON decode error.")

	
	def init_setting_smtp(self):
		self.load_data_from_json()
		try:
			with open('./config/config_perso.json', 'r') as f:
				self.config = json.load(f)
		except FileNotFoundError:
			messagebox.showerror("Erreur", "Fichier de configuration non trouvé.")
			self.config = {}
		
		self.entries = {}
		self.password_vars = {}  # Pour stocker les StringVar des mots de passe
		
		for i, (param_name, default_value) in enumerate(self.smtp_config.items()):
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
		self.load_data_from_json()
		options = list(self.email_templates.keys())
		email = self.test_email_config
		test_email = email.get('receiver_email_test')
		self.test_email_var.set(test_email)
		if options:
			self.selected_test_option.set(options[0])
		self.selected_test_option.set(options[0])
		
		select_menu = ttk.OptionMenu(self.frame_test_email, self.selected_test_option, options[0], *options)
		select_menu.grid(row=1, column=0, padx=5, pady=5)
		text = ttk.Label(self.frame_test_email, text="Envoyer un email de test à l'adresse email de TEST")
		text.grid(row=0, column=0, padx=5, pady=5)
		
		self.test_email_label = ttk.Label(self.frame_test_email, text="Envoyer a l'adresse email de test:")
		self.test_email_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
		text_input = ttk.Entry(self.frame_test_email, width=35, textvariable=self.test_email_var)
		text_input.grid(row=3, column=0, padx=5, pady=5)
		save_button_test_email = ttk.Button(self.frame_test_email, text="Enregistrer",
		                                    command=self.save_settings_test_email)
		send_test_email_button = ttk.Button(self.frame_test_email, text="Envoyer un email de test",
		                                    command=self.send_test_email)
		save_button_test_email.grid(row=4, column=0, padx=10, pady=5)
		send_test_email_button.grid(row=6, column=0, padx=10, pady=5)
	
	def init_setting_email(self):
		self.load_data_from_json()
		options = list(self.email_templates.keys())
	
		
		# Modification ici pour utiliser la nouvelle méthode update_email_content au lieu de load_data_from_json
		select_menu = ttk.OptionMenu(self.frame_email, self.selected_option, options[0], *options,
		                             command=self.update_email_content)
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
	
	def update_email_content(self, selection):
		email_template = self.email_templates.get(selection)
		if email_template:
			self.subject_entry.delete(0, tk.END)
			self.subject_entry.insert(0, email_template.get('subject', ''))
			self.body_text.delete('1.0', tk.END)
			self.body_text.insert('1.0', email_template.get('body', ''))
		else:
			# Effacer les champs si le template n'est pas trouvé
			self.subject_entry.delete(0, tk.END)
			self.body_text.delete('1.0', tk.END)
	
	def load_data_from_json(self):
		try:
			with open('./config/config_perso.json', 'r') as f:
				config = json.load(f)
			self.smtp_config = config.get("email", {})
			self.test_email_config = config.get("email_test", {})
			self.email_templates = config.get("email_templates", {})
		except FileNotFoundError:
			messagebox.showerror("Erreur", "Fichier de configuration non trouvé.")
			self.smtp_config = {}
			self.test_email_config = {}
			self.email_templates = {}

	def save_settings_smtp(self):
		try:
			smtp_settings = {
				param_name: entry.get()
				for param_name, entry in self.entries.items()
			}
			self.config["email"] = smtp_settings


			with open('./config/config_perso.json', 'w') as f:
				json.dump(self.config, f, indent=2)

			messagebox.showinfo("Enregistrés avec succès",
								   "Les paramètres SMTP ont été enregistrés avec succès")

			self.load_config()
		except Exception as e:
			messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement des données: {e}")
			logging.error(f"Erreur lors de l'enregistrement des données: {e}")

	
	def save_settings_email(self):
		try:
			with open('./config/config_perso.json', 'r') as f:
				current_config = json.load(f)
			
			selected_option = self.selected_option.get()
			email_template = {
				"subject": self.subject_entry.get(),
				"body": self.body_text.get("1.0", tk.END).strip()
			}
			
			if "email_templates" in current_config and selected_option in current_config["email_templates"]:
				current_config["email_templates"][selected_option].update(email_template)
			else:
				messagebox.showerror("Erreur", f"Le template d'email {selected_option} n'existe pas.")
				return
		
			with open('./config/config_perso.json', 'w') as f:
				json.dump(current_config, f, indent=2)
			messagebox.showinfo("Enregistrés avec succès", "Les paramètres ont été enregistrés avec succès")
			self.load_config()
		
		except Exception as e:
			messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement des données: {e}")
			logging.error(f"Setting email : Error {e}")
	
	
	def save_settings_test_email(self):
		try:
			new_test_email = self.test_email_var.get()
			self.test_email_config['receiver_email_test'] = new_test_email
			with open('./config/config_perso.json', 'r') as f:
				config = json.load(f)
			config['email_test']['receiver_email_test'] = new_test_email
			with open('./config/config_perso.json', 'w') as f:
				json.dump(config, f, indent=2)
			if new_test_email:
				messagebox.showinfo("Enregistrés avec succès", "Email de test enregistré avec succès")
		except Exception as e:
			messagebox.showerror("Erreur", f"Erreur lors de l'envoi de l'email de test: {e}")
			logging.error(f"Erreur lors d'enregistrement de l'email de test: {e}")
	def send_test_email(self):
		try:
			emailOpr = TestEmailSender()
			self.load_data_from_json()

			selected_test_option = self.selected_test_option.get()
			email_template = self.email_templates.get(selected_test_option)
			send_email = emailOpr.send_test_email(email_template['subject'], email_template['body'])
			if send_email:
				messagebox.showinfo("Email envoyé", "Email de test envoyé avec succès")
			else:
				messagebox.showerror("Erreur", "Erreur lors de l'envoi de l'email de test")
		
		except Exception as e:
			messagebox.showerror("Erreur", f"Erreur lors de l'envoi de l'email de test: {e}")
			logging.error(f"Erreur lors de l'envoi de l'email de test: {e}")

