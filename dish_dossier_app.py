from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp

from controller import DishDossierController
from model import DishDossierModel


class DishDossierApp(MDApp):
    def builder(self):
        model = DishDossierModel()
        controller = DishDossierController(model)
        return controller

