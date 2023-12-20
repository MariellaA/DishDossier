import kivy
import sqlite3 as sq
from kivy.core.window import Window
from kivy.uix.screenmanager import NoTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

from db_handler import DBHandler
# from controller import DishDossierController
from model import DishDossierModel
from kivy.config import Config
from recipe_api_handler import RecipeAPIHandler

Config.set('graphics', 'resizable', False)

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivymd.uix.list import OneLineAvatarListItem, MDList
from recipe import Recipe


# Builder.load_file('layouts/main_layout.kv')


class RecipeList(MDList):
    pass


class RecipeItem(OneLineAvatarListItem):
    pass


class ScreenOne(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenOne, self).__init__(**kwargs)

    def switch_screen(self):
        # print(self.manager)
        # self.manager.transition = NoTransition()
        self.manager.current = 'screen_two'

    def set_recipe_info(self, recipe):
        self.ids.recipe_title.text = recipe.title.upper()
        self.ids.recipe_prep_time.text = f"Prep. time: {recipe.prep_time if recipe.prep_time != -1 else 'N/A'}"
        self.ids.recipe_cook_time.text = f"Cook time: {recipe.cook_time if recipe.cook_time != -1 else 'N/A'}"
        self.ids.recipe_total_time.text = f"Total time: {recipe.total_cook_time if recipe.total_cook_time != -1 else 'N/A'}"
        self.ids.recipe_servings.text = f"Servings {recipe.servings if recipe.servings != -1 else 'N/A'}"
        # self.ids.recipe_descr.text = recipe.description
        self.ids.recipe_instr.text = f"Instructions:\n{recipe.instructions}"

        # Set Recipe Image and Ingredients
        self.ids.recipe_full_image.source = recipe.image_url if recipe.image_url else 'img_1.png'

        # Set Image button and label
        if recipe.favourite:
            self.ids.favs_button.icon = "heart"
            self.ids.favs_label.text = "Added to Favourites"
        else:
            self.ids.favs_button.icon = "heart-outline"
            self.ids.favs_label.text = "Add to Favourites"

        res = "Ingredients:\n"
        for ingredient in recipe.ingredients:
            res += f"{ingredient.ingredient}\n"
        self.ids.recipe_ingr.text = res


class ScreenTwo(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenTwo, self).__init__(**kwargs)

    def switch_screen(self):
        # self.manager.transition = NoTransition()
        self.manager.current = 'screen_one'


class DishDossierController(BoxLayout):
    pass


class DishDossierApp(MDApp):
    def __init__(self):
        super().__init__()
        self.api_handler = RecipeAPIHandler()
        self.model = DishDossierModel()
        self.db = DBHandler()
        self.selected_recipe_list = 'all_recipes'
        # self.load_random_recipe()
        # self.load_recipe_list_with_recipes()

        self.current_recipe = None

    def build(self):
        Window.size = (1280, 720)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.primary_hue = "200"  # "500"
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style_switch_animation_duration = 0.8

        return Builder.load_file('layouts/main_layout.kv')

    def show_data(self):
        pass

    def load_random_recipe(self):
        print('LOAD RECIPE FROM API')
        self.load_recipe_list_with_recipes()
        # recipes = self.api_handler.load_random_recipes_from_api()
        #
        # for recipe in recipes:
        #     print(recipe)
        #     # rec = Recipe(recipe)
        #
        #     # self.model.add_recipe(rec)
        #     # self.model.all_recipes.append(rec)
        #     recipe_data = {
        #         "recipe_api_id": recipe['id'],
        #         "title": recipe['title'],
        #         "prep_time": recipe['preparationMinutes'],
        #         "cook_time": recipe['cookingMinutes'],
        #         "total_cook_time": recipe['readyInMinutes'],
        #         "servings": recipe['servings'],
        #         "image_url": recipe['image'] if recipe['image'] != '' else 'img.png',
        #         "favourite": False,
        #         "original_recipe": False,
        #         "instructions": recipe['instructions'],
        #     }
        #
        #     ingredients_data = recipe['extendedIngredients']
        #
        #     recipe_exists = self.db.add_recipe(**recipe_data, ingredients_data=ingredients_data)
        #     # recipe_id = self.db.add_recipe(recipe_api_id, title, prep_time, cook_time, total_cook_time, servings, image,
        #     #                                favourite,
        #     #                                original_recipe, instructions, ingredients_data)
        #
        #     print(f"Recipe_ID: {recipe_exists}")

    def load_recipe_list_with_recipes(self, recipes):
        print('LOAD RECIPE FROM LIST')

        # recipes = self.db.get_all_recipes()
        print(f"ALL RECIPES:\n {recipes}")

        self.root.ids.recipe_list.clear_widgets()

        for recipe in recipes:
            # recipe = recipe_list[i]
            print(recipe.title)
            item = RecipeItem(id=str(recipe.recipe_api_id), text=recipe.title, size_hint_y=None, height=300)

            item.ids.recipe_img.source = recipe.image_url
            item.bind(on_release=self.on_recipe_select)

            self.root.ids.recipe_list.add_widget(item)

    def on_recipe_select(self, instance):
        print(self.root.ids.screen_one.ids)
        print(instance.id)
        recipe = self.db.get_recipe(instance.id)
        # recipe = self.model.search_for_recipe(instance.id, self.selected_recipe_list)[0]
        # print(recipe.title)
        # print(self.root.ids)
        self.current_recipe = recipe
        #
        print(f"TITLE: {recipe.title}")
        self.root.ids.screen_one.set_recipe_info(recipe)

    def on_recipe_list_select(self, list):
        # self.ids.recipe_list.clear_widgets()
        if list == "all_recipes":
            print("SELECT Sidebar")
            self.load_recipe_list_with_recipes(self.db.get_all_recipes())
            # self.load_recipe_list_with_recipes()
        elif list == "my_recipes":
            self.load_recipe_list_with_recipes(self.db.get_original_recipes())
        elif list == "favourites":
            print("SELECT Sidebar")
            self.load_recipe_list_with_recipes(self.db.get_all_favourite_recipes())

        self.selected_recipe_list = list

    def handle_search(self, search_str):
        print(search_str)
        self.root.ids.search_text.text = ""
        self.search_for_recipe(search_str)

    def search_for_recipe(self, look_for):
        res = self.model.search_for_recipe(look_for, self.selected_recipe_list)

        self.load_recipe_list_with_recipes(res)
        print(f"RES {res}")

    def add_or_remove_from_favourites(self):
        self.db.change_recipe_favourite_value(self.current_recipe)

        if not self.current_recipe.favourite:
            self.on_recipe_list_select(self.selected_recipe_list)

    def remove_from_favourites(self):
        self.current_recipe.favourite = False

        self.model.favourites.remove(self.current_recipe)
        self.on_recipe_list_select(self.selected_recipe_list)

    def on_scroll_stop(self, scroll_y):
        if scroll_y < 0.01:
            print(scroll_y)
            self.root.ids.show_more_btn.opacity = 1
            # self.load_random_recipe()
            # print("Scrolled to the end.")
        elif scroll_y > 0.1:
            self.root.ids.show_more_btn.opacity = 0
            # print("change opacity")

    def show_more_recipes(self):
        # print("show more")
        self.on_recipe_list_select(self.selected_recipe_list)
        self.root.ids.recipe_scroll.scroll_y = 1 - (1 / len(self.root.ids.recipe_list.children))

    def switch_screen(self):
        self.root.ids.screens.transition = NoTransition()

        if self.root.ids.screens.current == "screen_one":
            self.root.ids.screen_one.switch_screen()
        else:
            self.root.ids.screen_two.switch_screen()
        # print(self.root.ids.screens.current)

    def select_image(self):
        # Implement code to allow the user to select an image
        pass

    def remove_image(self):
        self.root.ids.recipe_full_image.source = ""
        self.image_source = ""

    # def _build_recipe_list(self):
    #     # Build the left column for the list of recipes
    #     for recipe in self.model.recipes:
    #         item = OneLineAvatarListItem(text=recipe['title'])
    #         item.add_widget(Image(source=recipe['image']))
    #         item.bind(on_release=self.on_recipe_select)
    #         self.recipe_list.add_widget(item)
    #
    #     self.add_widget(self.recipe_list)
    #
    # def _build_recipe_details(self):
    #     # Build the right column for displaying the details of the chosen recipe
    #     self.recipe_details.add_widget(Image())  # Placeholder for recipe image
    #     self.recipe_details.add_widget(OneLineAvatarListItem(text='Recipe Details'))
    #     self.add_widget(self.recipe_details)

    # def on_recipe_select(self, instance):
    #     # Handle the event when a recipe is selected from the list
    #     selected_recipe_index = self.recipe_list.children.index(instance)
    #     recipe_details = self.model.get_recipe_details(selected_recipe_index)
    #
    #     # Update the right column with the details of the selected recipe
    #     self.recipe_details.clear_widgets()
    #     self.recipe_details.add_widget(Image(source=recipe_details['image']))
    #     self.recipe_details.add_widget(OneLineAvatarListItem(text=recipe_details['title']))

    def switch_theme_style(self):
        self.theme_cls.primary_palette = (
            "Orange" if self.theme_cls.primary_palette == "Red" else "Red"
        )
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )
        # self.text_color = ("#252526" if self.theme_cls.theme_style == "Light" else "#ebebeb")
