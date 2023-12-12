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

        self.selected_recipe_list = 'all_recipes'
        self.load_recipe_list_with_recipes(self.model.all_recipes)

    def load_random_recipe(self):
        recipes = self.api_handler.load_random_recipe_from_api()

        for recipe in recipes:
            # data = {"id": recipe["id"], "title": recipe["title"],
            #         "prep_time": recipe["preparationMinutes"],
            #         "cooking_time": recipe["cookingMinutes"],
            #         "ready_in_time": recipe["readyInMinutes"],
            #         "servings": recipe["servings"],
            #         "image": "img_1.png",  # recipe["image"] if recipe["image"] else
            #         "instructions": recipe["instructions"]}
            print("Load random recipe")
            print(**recipe)
            print(recipe)
            rec = Recipe(recipe)
            self.model.recipes.append(rec)
            print(rec.title)
            print(self.recipe)

    def load_recipe_list_with_recipes(self, recipe_list):
        self.ids.recipe_list.clear_widgets()

        for recipe in recipe_list:
            # item = RecipeItem(text=f'title {i}', size_hint_y=None, height=item_height)
            # item = RecipeItem(id=recipe['id']), text=recipe['title'], size_hint_y=None, height=300)
            item = RecipeItem(id=recipe.id, text=recipe.title, size_hint_y=None, height=300)
            # item.bind(on_release=lambda rid=recipe['id']: self.on_recipe_select(rid))
            item.bind(on_release=self.on_recipe_select)
            item.ids.recipe_img.source =  recipe.image  # recipe['image']  # "img_1.png"
            self.ids.recipe_list.add_widget(item)
            # print(item.ids.recipe_img.source)
            # print(item.ids)
            # print(self.ids)

    def on_recipe_select(self, instance):
        print(instance.id)
        recipe = self.model.search_for_recipe(instance.id)
        self.ids.recipe_title.text = recipe.title.upper()
        self.ids.recipe_prep_time.text = f"Prep. time: {recipe.prep_time if recipe.prep_time != '-1' else 'N/A'}"
        self.ids.recipe_cook_time.text = f"Cook time: {recipe.cooking_time if recipe.cooking_time != '-1' else 'N/A'}"
        self.ids.recipe_total_time.text = f"Total time: {recipe.total_time if recipe.total_time != '-1' else 'N/A'}"
        self.ids.recipe_servings.text = f"Servings {recipe.servings if recipe.servings != '-1' else 'N/A'}"
        # self.ids.recipe_descr.text = recipe.description
        self.ids.recipe_instr.text = f"Instructions:\n{recipe.instructions}"
        # print(recipe['title'])
        print("select")

    def on_sidebar_select(self, list):
        ### The 'All Recipes' button gets pressed on initialization
        if list != self.selected_recipe_list:
            if list == "all_recipes":
                self.load_recipe_list_with_recipes(self.model.all_recipes)
            elif list == "my_recipes":
                self.load_recipe_list_with_recipes(self.model.my_recipes)
            elif list == "favorites":
                self.load_recipe_list_with_recipes(self.model.favorites)

            self.selected_recipe_list = list
            print("sidebar")
        print(list)



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
