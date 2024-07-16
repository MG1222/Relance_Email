import threading
import queue
import time
from tkinter import Frame, ttk, filedialog, messagebox
from PIL import Image, ImageTk
import logging
from app.email_operation import EmailOperation
from app.excel_operation import ExcelOperation
from app.parameters_page import ParametersPage


class MainPage(Frame):
	def __init__(self, parent, controller, *args, **kwargs):
		super().__init__(parent, *args, **kwargs)
		self.controller = controller
		self.excelOpr = ExcelOperation()
		self.emailOpr = EmailOperation()
		self.task_queue = queue.Queue()
		
		# Set up the main grid layout
		self.grid(row=0, column=0, sticky="nsew")
		self.grid_rowconfigure(1, weight=1)
		self.grid_columnconfigure(0, weight=1)
		
		self.create_widgets()
		self.starting_app()
		
		# Start the task handler thread
		self.controller.after(100, self.process_tasks)
	
	def create_widgets(self):
		# Create a frame for the tree view and other elements
		main_frame = Frame(self)
		main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
		main_frame.grid_rowconfigure(3, weight=1)
		main_frame.grid_columnconfigure(0, weight=1)
		
		# Add logo
		logo = Image.open("./asset/logo.png")
		logo.thumbnail((100, 100))
		logo = ImageTk.PhotoImage(logo)
		logo_label = ttk.Label(main_frame, image=logo)
		logo_label.image = logo
		logo_label.grid(row=0, column=0, pady=(0, 20), sticky="n")
		
		# Add description and version
		description = ttk.Label(main_frame,
		                        text="Mini app de gestion de données Excel avec vérification des doublons et envoi "
		                             "automatisé d'emails apres 3 mois, 6 mois et plus de 6 mois.",
		                        wraplength=400, justify="center")
		description.grid(row=1, column=0, pady=(0, 10), sticky="n")
		version = ttk.Label(main_frame, text="Version 1.0")
		version.grid(row=2, column=0, pady=(0, 20), sticky="n")
		
		# Configure the tree view
		self.tree = ttk.Treeview(main_frame, columns=(" ", "Nb", "Mois de Référence"), show="headings")
		self.tree.grid(row=3, column=0, sticky="nsew")
		
		# Create a frame for buttons
		buttons_frame = Frame(main_frame)
		buttons_frame.grid(row=4, column=0, pady=(20, 10), sticky="n")
		
		# Configure styles
		style = ttk.Style()
		style.configure("Treeview", rowheight=30)
		style.configure('W.TButton', font=('calibri', 10, 'bold', 'underline'), foreground='red')
		style.configure('TButton', font=('calibri', 10, 'bold'), foreground='blue')
		
		# Add buttons
		btn = ttk.Button(buttons_frame, text="Chercher", command=self.get_data)
		btn.grid(row=0, column=0, padx=10)
		
		parameter_button = ttk.Button(buttons_frame, text="Paramètres", style='W.TButton',
		                              command=lambda: self.controller.show_frame(ParametersPage.__name__))
		parameter_button.grid(row=0, column=1, padx=10)
		self.send_email_button = ttk.Button(buttons_frame, text="Envoyer des emails", command=self.try_send_email,
		                                    style='TButton', state="disabled")
		self.send_email_button.grid(row=0, column=2, padx=10)
		refresh_button = ttk.Button(buttons_frame, text="Rafraîchir", command=self.check_eligibility)
		refresh_button.grid(row=0, column=3, padx=10)
		
		# Create a frame for the progress bar
		self.progress_frame = Frame(self)
		self.progress_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
		self.progress = ttk.Progressbar(self.progress_frame, orient="horizontal", length=750, mode="determinate")
		self.progress.grid(row=0, column=4, sticky="ew")
		
		# Initially hide the progress bar
		self.progress.grid_remove()
	
	def starting_app(self):
		self.controller.title("Relance RH Email")
		
		# Configure columns for Treeview
		self.tree.heading(" ", text=" ")
		self.tree.heading("Nb", text="Nb")
		self.tree.heading("Mois de Référence", text="Mois de Référence")
		
		# Set column widths (adjust according to your content)
		self.tree.column(" ", width=200, anchor="center")
		self.tree.column("Nb", width=200, anchor="center")
		self.tree.column("Mois de Référence", width=200, anchor="center")
		
		self.check_eligibility()
	
	def try_send_email(self):
		self.progress["value"] = 0
		users = self.emailOpr.count_users()
		if users['three_months_count']['nb'] > 0 or users['six_months_count']['nb'] > 0 or users[
			'more_six_months_count']['nb'] > 0:
			self.progress.grid()
			self.task_queue.put((self.simulate_progress, (100, self.after_send_email)))
		else:
			messagebox.showinfo("Information", "Aucun email à envoyer.")
	
	def get_data(self):
		file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
		if file_path:
			logging.info(f"Dossier ouvert: {file_path}")
			self.progress.grid()
			self.progress["value"] = 5
			
			self.task_queue.put((self.process_excel_file, (file_path,)))
	
	def process_excel_file(self, file_path):
		save_bdd = self.excelOpr.process_excel_file(file_path)
		if save_bdd:
			self.simulate_progress(10, self.check_eligibility)
			messagebox.showinfo("Information", "Les données ont été insérées avec succès.")
		else:
			self.progress["value"] = 1
			self.controller.update_idletasks()
			time.sleep(0.5)
			if self.excelOpr.error_messages:
				messagebox.showerror("Erreur", "\n".join(self.excelOpr.error_messages))
			else:
				messagebox.showerror("Erreur", "Aucune donnée n'a été insérée dans la base de données")
		self.progress.grid_remove()
	
	def simulate_progress(self, steps, callback):
		for i in range(steps):
			time.sleep(0.1)
			self.progress["value"] = (i + 1) * (100 / steps)
			self.controller.update_idletasks()
		callback()
	
	def check_eligibility(self):
		try:
			users = self.emailOpr.count_users()
			
			self.tree.delete(*self.tree.get_children())
			self.tree.insert("", "end",
			                 values=("3 mois", users['three_months_count']['nb'], users['three_months_count'][
				                 'date']))
			self.tree.insert("", "end",
			                 values=("moins 3 mois", users['less_three_months']['nb'], " "))
			self.tree.insert("", "end",
			                 values=("6 mois", users['six_months_count']['nb'], users['six_months_count']['date']))
			self.tree.insert("", "end",
			                 values=("moins 6 mois", users['less_six_months']['nb'], " "))
			self.tree.insert("", "end", values=(
			"+ 6 mois", users['more_six_months_count']['nb'], " "))
			
			if users['three_months_count']['nb'] > 0 or users['six_months_count']['nb'] > 0 or users[
				                                                                                   'more_six_months_count']['nb'] > 0:
				self.send_email_button.config(state="normal")
			
			tree_height = min(6, len(self.tree.get_children()))
			self.tree.config(height=tree_height)
	
		
		except Exception as e:
			logging.error(f"Error: {e}")
			self.tree.delete(*self.tree.get_children())
			self.tree.insert("", "end", values=("", "Aucun utilisateur dans la base de donne", ""))
			self.tree.config(height=1)
			self.send_email_button.config(state="disabled")
	
	def after_send_email(self):
		send_email = self.emailOpr.try_send_email()
		
		if send_email:
			messagebox.showinfo("Information", "Les emails ont été envoyés avec succès.")
			self.send_email_button.config(state="disabled")
			self.check_eligibility()
			self.progress.grid_remove()
		else:
			messagebox.showerror("Erreur", "Aucun email n'a été envoyé.")
	
	def process_tasks(self):
		while not self.task_queue.empty():
			task, args = self.task_queue.get()
			task(*args)
		self.controller.after(100, self.process_tasks)
