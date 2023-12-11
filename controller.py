# dish_dossier_controller.py
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivymd.uix.list import OneLineAvatarListItem, MDList, OneLineListItem, OneLineAvatarIconListItem, \
    OneLineIconListItem
from kivymd.uix.navigationrail import MDNavigationRail, MDNavigationRailItem
from kivymd.uix.boxlayout import MDBoxLayout

from Recipe import Recipe

Builder.load_file('layouts/main_layout.kv')


class RecipeList(MDList):
    pass


class RecipeItem(OneLineAvatarListItem):
    pass
    # def __init__(self, **kwargs):
    #     super(RecipeItem, self).__init__(**kwargs)
    # self.img = StringProperty("img.png")


class DishDossierController(BoxLayout):
    def __init__(self, app, model, api_handler, **kwargs):
        super(BoxLayout, self).__init__(**kwargs)
        self.app = app
        self.model = model
        self.api_handler = api_handler

        # self.recipe_list = RecipeList()
        self.load_recipe_list_with_recipes()

        # self.model.load_recipes_from_api()  # Load recipes when the app starts

        # Initialize UI components
        # self.sidebar = MDNavigationRail(id='nav_rail')
        # self.recipe_list = MDBoxLayout(orientation='vertical', spacing=10)
        # self.recipe_details = MDBoxLayout(orientation='vertical', spacing=10)

    def load_random_recipe(self):
        recipes = self.api_handler.load_random_recipe_from_api()

        for recipe in recipes:
            data = {"id": recipe["id"], "title": recipe["title"],
                    "prep_time": recipe["preparationMinutes"],
                    "cooking_time": recipe["cookingMinutes"],
                    "ready_in_time": recipe["readyInMinutes"],
                    "servings": recipe["servings"],
                    "image": "img_1.png",  # recipe["image"] if recipe["image"] else
                    "instructions": recipe["instructions"]}

            self.model.recipes.append(Recipe(**data))
            print(self.recipe)

    def load_recipe_list_with_recipes(self):
        self.ids.recipe_list.clear_widgets()

        for recipe in self.model.recipes:
            # item = RecipeItem(text=f'title {i}', size_hint_y=None, height=item_height)
            item = RecipeItem(text=recipe['title'], size_hint_y=None, height=300)

            # print(recipe['title'])
            # print(recipe['image'])
            item.bind(on_release=self.on_recipe_select)
            item.ids.recipe_img.source = recipe['image']  # "img_1.png"
            self.ids.recipe_list.add_widget(item)
            # print(item.ids.recipe_img.source)
            # print(item.ids)
            # print(self.ids)

    def on_recipe_select(self, instance):
        print("select")

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
        self.app.theme_cls.primary_palette = (
            "Orange" if self.app.theme_cls.primary_palette == "Red" else "Red"
        )
        self.app.theme_cls.theme_style = (
            "Dark" if self.app.theme_cls.theme_style == "Light" else "Light"
        )
        # self.app.text_color = ("#252526" if self.app.theme_cls.theme_style == "Light" else "#ebebeb")

# from kivy.lang import Builder
# from kivy.properties import ListProperty
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.widget import Widget
# from kivymd.uix.boxlayout import MDBoxLayout
# from kivymd.uix.list import OneLineListItem
# #
# Builder.load_file('layouts/main_layout.kv')
#
#
# # class SideBarLayout(Widget):
# #     pass
# class DishDossierController(MDBoxLayout):
#     def __init__(self, app, model, *args, **kwargs):
#         super().__init__(**kwargs)
#         self.model = model
#         self.app = app
#
#         print(kwargs)
#         print(self.app)
#         # self.recipe_list = self.ids.recipe_list
#
#     def on_navigation_item_select(self, item_name):
#         # Handle navigation item selection here
#         print(f"Selected: {item_name}")
#
#     def load_initial_recipes(self):
#         self.model.load_initial_recipes()
#         self.update_recipe_list()
#
#     def load_more_recipes(self):
#         self.model.load_recipes(len(self.model.recipes), 5)
#         self.update_recipe_list()
#
#     def update_recipe_list(self):
#         self.recipe_list.clear_widgets()
#         for recipe in self.model.recipes:
#             item = OneLineListItem(text=recipe)
#             self.recipe_list.add_widget(item)
#
#     def switch_theme_style(self):
#         self.app.theme_cls.primary_palette = (
#             "Orange" if self.app.theme_cls.primary_palette == "Red" else "Red"
#         )
#         self.app.theme_cls.theme_style = (
#             "Dark" if self.app.theme_cls.theme_style == "Light" else "Light"
#         )
#         # self.app.text_color = ("#252526" if self.app.theme_cls.theme_style == "Light" else "#ebebeb")
