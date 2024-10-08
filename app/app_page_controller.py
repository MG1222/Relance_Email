import logging
from tkinter import Tk

from app.view.database_page import DatabasePage
from app.view.main_page import MainPage
from app.view.parameters_page import ParametersPage


class AppPageController(Tk):
    """
    This class is the controller of the application. It manages the different pages of the application.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frames = {}

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        for F in (MainPage, ParametersPage, DatabasePage):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=1, column=0, sticky="nsew")

        self.show_frame("MainPage")

    def show_frame(self, page_name):

        if page_name in self.frames:
            frame = self.frames[page_name]
            frame.tkraise()
            if page_name == "ParametersPage":
                self.geometry("860x850")
            else:
                self.geometry("800x600")
        else:
            logging.error(f"appController = Page not found {page_name}.")
            print(f"Page {page_name} non trouvée.")
