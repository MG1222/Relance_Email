import json
import threading
import queue
import time
from tkinter import Frame, ttk, filedialog, messagebox
from PIL import Image, ImageTk
import logging
from app.email_operation import EmailOperation
from app.excel_operation import ExcelOperation
from app.parameters_page import ParametersPage
from app.database import Database


class MainPage(Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.file_path_label = None
        self.controller = controller
        self.bdd = Database()
        self.excelOpr = ExcelOperation()
        self.emailOpr = EmailOperation()
        self.task_queue = queue.Queue()


        self.progress_label = ttk.Label(self, text="Progress: ")
        # Set up the main grid layout
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()
        self.starting_app()
        self.display_last_path()

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
                                 "automatisé d'emails apres 3 mois, 6 mois et 12 mois.",
                            wraplength=400, justify="center")
        description.grid(row=1, column=0, pady=(0, 10), sticky="n")
        version = ttk.Label(main_frame, text="Version 1.0")
        version.grid(row=2, column=0, pady=(0, 20), sticky="n")

        info_button = ttk.Button(main_frame, text="?", width=1)
        info_button.config(command=lambda: messagebox.showinfo("Information",
                                                               "La table affiche des informations sur l'envoi d'e-mails basé sur la durée depuis la dernière relance (4, 7, 12 mois) et le total des e-mails envoyés. Chaque ligne indique le nombre d'e-mails à envoyer ou à ne pas envoyer pour chaque période, ainsi que le total général."))
        info_button.grid(row=2, column=0, sticky="en")

        # Configure the tree view
        self.tree = ttk.Treeview(main_frame,
                                 columns=("Relance à", "Envoyer mail", "Pas envoyer mail", "Total e-mails envoyés"),
                                 show="headings")
        self.tree.grid(row=3, column=0, sticky="nsew")

        # Create a frame for buttons
        buttons_frame = Frame(main_frame)
        buttons_frame.grid(row=4, column=0, pady=(20, 10), sticky="n")

        # Configure styles
        style = ttk.Style()
        style.configure("Treeview", rowheight=30)
        style.configure('Treeview.Heading', font=('calibri', 10, 'bold'))

        style.configure('W.TButton', font=('calibri', 10, 'bold', 'underline'), foreground='red')
        style.configure('TButton', font=('calibri', 10, 'bold'), foreground='blue')

        # Add buttons
        btn = ttk.Button(buttons_frame, text="Chercher", command=self.get_data)
        btn.grid(row=0, column=0, padx=10)

        parameter_button = ttk.Button(buttons_frame, text="Paramètres", style='W.TButton',
                                      command=lambda: self.controller.show_frame(ParametersPage.__name__))
        parameter_button.grid(row=0, column=1, padx=10)
        self.send_email_button = ttk.Button(buttons_frame, text="Envoyer des emails", command=self.confirm_send_email,
                                            style='TButton', state="disabled")
        self.send_email_button.grid(row=0, column=2, padx=10)
        refresh_button = ttk.Button(buttons_frame, text="Rafraîchir", command=self.check_eligibility)
        refresh_button.grid(row=0, column=3, padx=10)
        # Create and configure the progress bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        # Initially, you might want to hide the progress bar until needed
        self.progress.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        self.progress.grid_remove()

        self.footer_frame = Frame(self)
        self.footer_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
        self.file_path_label = ttk.Label(self.footer_frame, text="Dernier fichier traité: ")
        self.file_path_label.grid(row=0, column=0, sticky="w")



    def starting_app(self):
        self.controller.title("Relance RH Email")
        # Configure columns for Treeview
        self.tree.heading("Relance à", text="Relance à")
        self.tree.heading("Envoyer mail", text="Envoyer mail")
        self.tree.heading("Pas envoyer mail", text="Pas envoyer mail")
        self.tree.heading("Total e-mails envoyés", text="Total e-mails envoyés")

        # Set column widths (adjust according to your content)
        self.tree.column("Relance à", width=150, anchor="center")
        self.tree.column("Envoyer mail", width=200, anchor="center")
        self.tree.column("Pas envoyer mail", width=150, anchor="center")
        self.tree.column("Total e-mails envoyés", width=150, anchor="center")

        self.check_eligibility()
    def display_last_path(self):
        self.get_current_file_path()

    def get_current_file_path(self):
        last_path = self.bdd.get_last_path()
        if last_path is None:
            display_text = "Aucun fichier traité"
        else:
            display_text = last_path

        # Mise à jour du texte du label directement
        self.file_path_label.config(text=f"Dernier fichier traité: {display_text}")

        return display_text

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
            messagebox.showinfo("Information", "Les données ont été insérées avec succès.")
            self.bdd.insert_path(file_path)
            self.check_eligibility()

            self.file_path_label.config(text=f"Dernier fichier traité: {self.get_current_file_path()}")
        else:
            self.progress["value"] = 1
            self.controller.update_idletasks()
            time.sleep(0.5)
            if self.excelOpr.error_messages:
                messagebox.showerror("Erreur", "\n".join(self.excelOpr.error_messages))
            else:
                messagebox.showerror("Erreur", "Aucune donnée n'a été insérée dans la base de données")
        self.progress.grid_remove()
        self.check_eligibility()

    def check_eligibility(self):
        try:
            style = ttk.Style()
            style.configure("Blue.Foreground", foreground="blue")
            users = self.emailOpr.count_users()
            total_email = self.bdd.get_total_email_send()
            self.tree.delete(*self.tree.get_children())

            self.tree.insert("", "end",
                             values=(f"4 mois ({users['three_months_count']['date']})", users['three_months_count'][
                                 'nb'],
                                     users['less_three_months'][
                                         'nb']),
                             tags=('Envoyer mail', 'Pas envoyer mail'))
            self.tree.insert("", "end",
                             values=(f"7 mois ({users['six_months_count']['date']})", users['six_months_count'][
                                 'nb'], users['less_six_months'][
                                         'nb']),
                             tags=('Envoyer mail', 'Pas envoyer mail'))
            self.tree.insert("", "end",
                             values=(
                                 f"12 mois ({users['twelve_months_count']['date']})",
                                 users['twelve_months_count']['nb'],
                                 users['less_twelve_months'][
                                     'nb']),
                             tags=('Envoyer mail', 'Pas envoyer mail'))
            self.tree.insert("", "end",
                             values=("Total ", users['send_email'], users['dont_send_email'], total_email),
                             tags=('Total e-mails envoyés',))

            if users['three_months_count']['nb'] > 0 or users['six_months_count']['nb'] > 0 or \
                    users['twelve_months_count']['nb'] > 0:
                self.send_email_button.config(state="normal")

            tree_height = min(6, len(self.tree.get_children()))
            self.tree.config(height=tree_height)


        except Exception as e:
            logging.error(f"Error: {e}")
            self.tree.delete(*self.tree.get_children())
            self.tree.insert("", "end", values=("", "Aucun utilisateur dans la base de donne", ""))
            self.tree.config(height=1)
            self.send_email_button.config(state="disabled")

    def process_tasks(self):
        while not self.task_queue.empty():
            task, args = self.task_queue.get()
            task(*args)
        self.controller.after(100, self.process_tasks)

    def send_emails_with_progress(self, total_emails, users):
        self.progress_frame = Frame(self)
        self.progress_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        self.progress = ttk.Progressbar(self.progress_frame, orient="horizontal", length=750, mode="determinate")
        self.progress.grid(row=1, column=0, sticky="ew")
        self.text_progress = ttk.Label(self.progress_frame, text="Progress: ")
        self.text_progress.grid(row=0, column=0, sticky="s")

        def update_progress(email_count, total_emails):
            progress_value = (email_count / total_emails) * 100
            self.progress["value"] = progress_value
            self.text_progress.config(text="Progress: {}/{} ({:.2f}%)".format(email_count, total_emails,
                                                                              progress_value))
            self.controller.update_idletasks()

        self.emailOpr.try_send_email(update_progress)
        self.after_send_email()

    def confirm_send_email(self):
        users = self.emailOpr.count_users()
        total_emails = users['send_email']
        if total_emails > 0:
            confirm = messagebox.askyesno("Confirmation", "Voulez-vous vraiment envoyer les emails ?")
            if confirm:
                self.send_emails_with_progress(total_emails, users['users'])
                self.check_eligibility()
            else:
                messagebox.showinfo("Annulé", "L'envoi des emails a été annulé.")
                self.check_eligibility()
        else:
            messagebox.showinfo("Information", "Aucun email à envoyer.")

    def after_send_email(self):
        self.progress_frame.grid_remove
        self.text_progress.grid_remove()
        self.progress.grid_remove()
        self.check_eligibility()
        messagebox.showinfo("Information", "Les emails ont été envoyés avec succès.")
        self.send_email_button.config(state="disabled")



