import logging

from app.database import Database

from tkinter import Frame, Label, Entry, Button, ttk, StringVar, Toplevel, OptionMenu, messagebox
import tkinter as tk


class DatabasePage(Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.controller = controller
        self.bdd = Database()

        self.search_by = StringVar(value="nom")

        self.create_frames()
        self.get_all_users()


    def create_frames(self):
        # Main frame to contain all sub-frames
        main_frame = Frame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Frame 1: Search bar
        search_frame = Frame(main_frame)
        search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        label = ttk.Label(search_frame, text="Chercher:")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.search_bar = Entry(search_frame)
        self.search_bar.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.search_bar.bind("<KeyRelease>", self.search)

        # Add checkboxes for search criteria
        self.nom_checkbox = ttk.Radiobutton(search_frame, text="Nom", variable=self.search_by, value="nom")
        self.nom_checkbox.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.email_checkbox = ttk.Radiobutton(search_frame, text="Email", variable=self.search_by, value="email")
        self.email_checkbox.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Frame 2: Table
        table_frame = Frame(main_frame)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = ("id", "last_name", "first_name", "email", "last_interview", "dont_email")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("last_name", text="Nom")
        self.tree.heading("first_name", text="Prenom")
        self.tree.heading("email", text="Email")
        self.tree.heading("last_interview", text="Dernier entretien")
        self.tree.heading("dont_email", text="Email Permission")

        # Adjust column widths to be more compact
        self.tree.column("id", width=30, anchor="center")
        self.tree.column("last_name", width=120, anchor="center")
        self.tree.column("first_name", width=120, anchor="center")
        self.tree.column("email", width=200, anchor="center")
        self.tree.column("last_interview", width=150, anchor="center")
        self.tree.column("dont_email", width=100, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.tree.bind("<Double-1>", self.on_double_click)

        # Add a scrollbar to the table
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Frame 3: Filter checkboxes and return button
        filter_frame = Frame(main_frame)
        filter_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        filter_frame.grid_columnconfigure(0, weight=1)

        filter_label = ttk.Label(filter_frame, text="Sélectionnez les candidats :")
        filter_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.can_send_var = tk.BooleanVar()
        self.cannot_send_var = tk.BooleanVar()

        can_send_checkbox = ttk.Checkbutton(filter_frame, text="à qui on NE peut PAS envoyer des emails",
                                            variable=self.can_send_var, command=self.update_checkboxes)
        can_send_checkbox.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        cannot_send_checkbox = ttk.Checkbutton(filter_frame, text="à qui on PEUT envoyer des emails",
                                               variable=self.cannot_send_var, command=self.update_checkboxes)
        cannot_send_checkbox.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        # Button
        get_all_users_button = ttk.Button(filter_frame, text="Rafraîchir",
                                          command=self.get_all_users)
        get_all_users_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        return_button = ttk.Button(filter_frame, text="Retour", command=lambda: self.controller.show_frame("MainPage"))
        return_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        checkbox_button = ttk.Button(filter_frame, text="Chercher", command=self.filter_users)
        checkbox_button.grid(row=3, column=0, padx=5, pady=5, sticky="w")

    def update_checkboxes(self):
        if self.can_send_var.get():
            self.cannot_send_var.set(False)
        elif self.cannot_send_var.get():
            self.can_send_var.set(False)

    def filter_users(self):
        users = self.bdd.get_all_users()
        self.tree.delete(*self.tree.get_children())
        for user in users:
            user = list(user)
            dont = user[5]
            if (self.can_send_var.get() and dont == 1) or (self.cannot_send_var.get() and dont == 0):
                user[5] = "Ne peut pas !" if user[5] == 1 else "Peut envoyer"
                self.tree.insert("", "end", values=user)


    def on_double_click(self, event):
        item = self.tree.selection()[0]
        column = self.tree.identify_column(event.x)
        column_index = int(column.replace('#', '')) - 1
        column_name = self.get_column_text(column_index)

        self.edit_window = Toplevel(self)
        self.edit_window.title("Edit Cell")

        if column_name == "Email Permission":
            Label(self.edit_window, text="Edit Email Permission:").grid(row=0, column=0, padx=5, pady=5)
            self.new_value = StringVar()
            options = ["Ne peut pas !", "Peut envoyer"]
            OptionMenu(self.edit_window, self.new_value, *options).grid(row=0, column=1, padx=5, pady=5)
            current_value = self.tree.item(item, "values")[column_index]
            self.new_value.set(current_value)
        else:
            Label(self.edit_window, text=f"Edit {column_name}:").grid(row=0, column=0, padx=5, pady=5)
            self.new_value = StringVar()
            Entry(self.edit_window, textvariable=self.new_value).grid(row=0, column=1, padx=5, pady=5)
            self.new_value.set(self.tree.item(item, "values")[column_index])

        Button(self.edit_window, text="Save", command=lambda: self.save_edit(item, column_index)).grid(row=1, column=0,
                                                                                                       columnspan=2,
                                                                                                       pady=5)

    def save_edit(self, item, column_index):
        new_value = self.new_value.get()
        values = list(self.tree.item(item, "values"))

        if self.tree["columns"][column_index] == "dont_email":
            if new_value not in ["Ne peut pas !", "Peut envoyer"]:
                tk.messagebox.showerror("Invalid Input", "S'il vous plaît, entrez 'Ne peut pas !' ou 'Peut envoyer'")
                return
            values[column_index] = new_value
            db_value = 1 if new_value == "Ne peut pas !" else 0
        else:
            values[column_index] = new_value
            db_value = new_value

        self.tree.item(item, values=values)

        user_id = self.tree.item(item, "values")[0]
        column_name = self.tree["columns"][column_index]
        self.bdd.update_user(user_id, column_name, db_value)

        self.edit_window.destroy()

    def get_column_text(self, column_index):
        column_name = self.tree["columns"][column_index]

        # Map column names to French
        column_name_map = {
            "id": "ID",
            "last_name": "Nom",
            "first_name": "Prenom",
            "email": "Email",
            "last_interview": "Dernier entretien",
            "dont_email": "Email Permission"
        }

        return column_name_map.get(column_name, column_name)

    def get_all_users(self):
        try:
            users = self.bdd.get_all_users()
            self.tree.delete(*self.tree.get_children())
            if not users:
                self.tree.insert("", "end", values=["", "", "", "Aucun candidates", "", ""])
            else:
                for user in users:
                    user = list(user)
                    user[5] = "Ne peut pas !" if user[5] == 1 else "Peut envoyer"
                    self.tree.insert("", "end", values=user)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {'{'}\n{'}'.join(e.args)}")
            logging.error(e)



    def search(self, event=None):
        search_term = self.search_bar.get()
        search_by = self.search_by.get()

        if search_by == "nom":
            users = self.bdd.get_users_by_name(search_term)
        else:
            users = self.bdd.get_users_by_email(search_term)

        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert the filtered users with descriptive dont
        for user in users:
            user = list(user)
            user[5] = "Ne peut pas !" if user[5] == 1 else "Peut envoyer"
            self.tree.insert("", "end", values=user)


