import kivy
from kivy.core.window import Window
from kivymd.app import MDApp
from controller import DishDossierController
from model import DishDossierModel
from kivy.config import Config

from recipe_api_handler import RecipeAPIHandler

Config.set('graphics', 'resizable', False)


class DishDossierApp(MDApp):
    def build(self):
        Window.size = (1280, 720)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.primary_hue = "200"  # "500"
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style_switch_animation_duration = 0.8

        api_handler = RecipeAPIHandler()
        model = DishDossierModel()
        controller = DishDossierController(self, model, api_handler)
        return controller

#
# if __name__ == "__main__":
#     DishDossierApp().run()
