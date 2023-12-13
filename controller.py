from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivymd.uix.list import OneLineAvatarListItem, MDList
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
        # self.load_random_recipe()
        self.load_recipe_list_with_recipes(self.model.all_recipes)

        self.current_recipe = None

    def load_random_recipe(self):
        recipes = self.api_handler.load_random_recipes_from_api()

        for recipe in recipes:
            # print(recipe)
            rec = Recipe(recipe)

            self.model.all_recipes.append(rec)
            self.load_recipe_list_with_recipes(self.model.all_recipes)

    def load_recipe_list_with_recipes(self, recipe_list):
        print('LOAD RECIPE FROM LIST')
        self.ids.recipe_list.clear_widgets()
        print(recipe_list)
        for recipe in recipe_list:
            print(recipe.id)
            item = RecipeItem(id=recipe.id, text=recipe.title, size_hint_y=None, height=300)

            item.ids.recipe_img.source = recipe.image
            item.bind(on_release=self.on_recipe_select)

            self.ids.recipe_list.add_widget(item)

    def on_recipe_select(self, instance):
        recipe = self.model.search_for_recipe(instance.id, self.selected_recipe_list)[0]
        print(recipe)
        self.current_recipe = recipe

        print(recipe.title)
        self.ids.recipe_title.text = recipe.title.upper()
        self.ids.recipe_prep_time.text = f"Prep. time: {recipe.prep_time if recipe.prep_time != '-1' else 'N/A'}"
        self.ids.recipe_cook_time.text = f"Cook time: {recipe.cooking_time if recipe.cooking_time != '-1' else 'N/A'}"
        self.ids.recipe_total_time.text = f"Total time: {recipe.total_time if recipe.total_time != '-1' else 'N/A'}"
        self.ids.recipe_servings.text = f"Servings {recipe.servings if recipe.servings != '-1' else 'N/A'}"
        # self.ids.recipe_descr.text = recipe.description
        self.ids.recipe_instr.text = f"Instructions:\n{recipe.instructions}"

        # Set Recipe Image and Ingredients
        self.ids.recipe_full_image.source = recipe.image

        # Set Image button and label
        if recipe.favourite:
            self.ids.favs_button.icon = "heart"
            self.ids.favs_label.text = "Added to Favourites"
        else:
            self.ids.favs_button.icon = "heart-outline"
            self.ids.favs_label.text = "Add to Favourites"

        res = "Ingredients:\n"
        for ingredient in recipe.extendedIngredients:
            res += f"{ingredient['original']}\n"
        self.ids.recipe_ingr.text = res
        print("select")

    def on_recipe_list_select(self, list):
        # if list != self.selected_recipe_list:
        if list == "all_recipes":
            self.load_recipe_list_with_recipes(self.model.all_recipes)
        elif list == "my_recipes":
            self.load_recipe_list_with_recipes(self.model.my_recipes)
        elif list == "favourites":
            self.load_recipe_list_with_recipes(self.model.favourites)

        self.selected_recipe_list = list
        print("sidebar")
        print(list)

    def handle_search(self, search_str):
        print(search_str)
        self.ids.search_text.text = ""
        self.search_for_recipe(search_str)

    def search_for_recipe(self, look_for):
        res = self.model.search_for_recipe(look_for, self.selected_recipe_list)

        self.load_recipe_list_with_recipes(res)
        print(f"RES {res}")

    def add_to_favourites(self):
        self.model.favourites.append(self.current_recipe)
        self.current_recipe.favourite = True

    def remove_from_favourites(self):
        self.current_recipe.favourite = False

        self.model.favourites.remove(self.current_recipe)
        self.on_recipe_list_select(self.selected_recipe_list)

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
