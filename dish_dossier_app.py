import os
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import NoTransition
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from kivy.config import Config
from kivy.lang import Builder
from views import RecipeCard, FilterItem, DialogContent

Config.set('graphics', 'resizable', False)
Config.set('kivy', 'window_icon', 'images/start_logo.png')


class DishDossierApp(MDApp):
    def __init__(self, api_handler, db):
        super().__init__()
        self.api_handler = api_handler
        self.db = db

        self.selected_recipe_list = 'all_recipes'

        self.search_menu = None
        self.add_menu = None
        self.url_window = None
        self.export_menu = None
        self.export_window = None
        self.current_recipe = None
        self.potentially_search_api = False

        self.search_selection = []
        self.offset = 0
        self.page_size = 6
        self.look_for = ""

    def build(self):
        Window.size = (1280, 720)

        # Calculate the center position based on screen size and window size
        screen_width, screen_height = Window.size
        window_width, window_height = Window.system_size

        x = (screen_width - window_width) / 2.7
        y = (screen_height - window_height) / 2.8

        Window.left = x
        Window.top = y

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_hue = "200"
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style_switch_animation_duration = 0.8

        return Builder.load_file('layouts/view.kv')

    def on_start(self):
        add_items = [
            {"icon": "pencil-plus-outline",
             "viewclass": "MDRectangleFlatIconButton",
             "text": "Manually",
             "on_release": lambda: (self.switch_screen(), self.add_menu.dismiss()),
             "line_color": (0, 0, 0, 0),
             "theme_text_color": "Custom",
             "text_color": (0.9765, 0.9686, 0.8745, 1),
             "icon_color": (0.65098, 0.35294, 0, 1)
             },
            {"icon": "link-variant-plus",
             "viewclass": "MDRectangleFlatIconButton",
             "text": "Use URL",
             "on_release": lambda: (self.show_url_window(), self.add_menu.dismiss()),
             "line_color": (0, 0, 0, 0),
             "theme_text_color": "Custom",
             "icon_color": (0.65098, 0.35294, 0, 1),
             "text_color": (0.9765, 0.9686, 0.8745, 1),
             },
        ]

        export_items = [
            {"icon": "file-export-outline",
             "viewclass": "MDRectangleFlatIconButton",
             "text": "Export as PDF",
             "on_release": lambda: (self.export(), self.export_menu.dismiss()),
             "line_color": (0, 0, 0, 0),
             "theme_text_color": "Custom",
             "text_color": (0.9765, 0.9686, 0.8745, 1),
             "icon_color": (0.65098, 0.35294, 0, 1)
             },
            {"icon": "email-fast-outline",
             "viewclass": "MDRectangleFlatIconButton",
             "text": "Send by Email",
             "on_release": lambda: (self.show_email_input_window(), self.export_menu.dismiss()),
             "line_color": (0, 0, 0, 0),
             "theme_text_color": "Custom",
             "icon_color": (0.65098, 0.35294, 0, 1),
             "text_color": (0.9765, 0.9686, 0.8745, 1),
             },
        ]

        self.add_menu = MDDropdownMenu(
            caller=self.root.ids.drop_item,
            items=add_items,
            width_mult=2,
            background_color=(0.2392, 0.2196, 0.1725, 1),
            size_hint=(None, None),
            max_height=dp(75),
        )

        self.export_menu = MDDropdownMenu(
            caller=self.root.ids.screen_one.ids.export_btn,
            items=export_items,
            width_mult=2,
            background_color=(0.2392, 0.2196, 0.1725, 1),
            size_hint=(None, None),
            max_height=dp(75),
        )

    def write_an_email(self, instance):
        print("Email sent!")
        print(self.export_window.content_cls.ids.window_input.text)
        self.export_window.content_cls.ids.window_input.text = ""
        self.export_window.dismiss()

    def load_random_recipe(self, recipe_count):
        recipes_data = self.api_handler.load_random_recipes_from_api(recipe_count)
        recipe_info = self.extract_information(recipes_data)

        recipes = []

        for recipe_info in recipes_data:
            recipe_exists = self.db.add_recipe(**recipe_info)

            if recipe_exists:
                recipes.append(recipe_exists)
        return recipes

    def load_found_recipe(self, search_by, look_for, recipe_count):
        found_recipes = self.api_handler.find_recipe_from_api(search_by, look_for, recipe_count)
        recipe_info = self.extract_information(found_recipes)

        recipes = []

        for recipe_info in recipe_info:
            recipe_exists = self.db.add_recipe(**recipe_info)

            if recipe_exists:
                recipes.append(recipe_exists)

        return recipes

    def load_recipe_list_with_recipes(self, recipes):
        if not recipes:
            self.show_show_more_btn(False)
        else:
            # Display the recipes (customize this part based on your UI)
            for recipe in recipes:
                recipe_card = RecipeCard(id=str(recipe.recipe_api_id), )

                recipe_card.ids.recipe_img.source = recipe.image_url
                recipe_card.ids.recipe_title_btn.text = recipe.title
                recipe_card.bind(on_release=self.on_recipe_select)

                self.root.ids.recipe_list.add_widget(recipe_card)

                if self.offset == 0:
                    self.root.ids.recipe_scroll.scroll_y = 1

                self.offset += 1

    def on_recipe_select(self, instance):
        try:
            if instance.id != "None":
                recipe = self.db.get_recipe(instance.id)
            else:
                title = instance.ids.recipe_title_btn.text
                recipe = self.db.get_original_recipe(title)
        except AttributeError:
            recipe = instance

        self.current_recipe = recipe

        if self.current_recipe.original_recipe:
            self.root.ids.screen_one.switch_on_delete_edit_btn(True)

        self.root.ids.screen_one.set_recipe_info(recipe)

    def reset_search_values(self):
        self.root.ids.recipe_list.clear_widgets()
        self.offset = 0
        self.potentially_search_api = False
        self.root.ids.search_text.text = ""
        self.search_selection = []
        self.root.ids.recipe_scroll.scroll_y = 1
        self.show_more_btn_on_scroll(self.root.ids.recipe_scroll.scroll_y)

    def on_recipe_list_select(self, list):
        if self.selected_recipe_list != list:
            self.reset_search_values()

        if list == "all_recipes":

            self.potentially_search_api = True
            # print(f"SEARCH BAR CONTENT {self.root.ids.search_text.text}")
            search_criteria = self.get_search_criteria()

            if self.root.ids.search_text.text != "" or search_criteria != ["title"]:
                # print("SEARCH API ON_RECIPE_LIST_SELECT")
                recipes = self.search_filtered_recipes_from_db(self.get_search_criteria(),
                                                               self.root.ids.search_text.text,
                                                               False, True, False)
                print(recipes)
                if not recipes:
                    # print("NO RECIPES IN DB ON_RECIPE_LIST_SELECT")
                    found_recipes = self.search_filtered_recipes_from_api(self.get_search_criteria(),
                                                                          self.root.ids.search_text.text, 3)

                    if found_recipes:
                        self.load_recipe_list_with_recipes(found_recipes)
            else:
                if not self.check_if_there_are_more_recipes_to_show():
                    # print("LOADING RANDOM ON_RECIPE_LIST_SELECT")
                    random_recipes = self.load_random_recipe(6)

                    if random_recipes:
                        self.load_recipe_list_with_recipes(random_recipes)
                else:
                    self.load_recipe_list_with_recipes(self.db.get_recipes(self.offset, self.page_size))
            self.root.ids.screen_one.switch_on_delete_edit_btn(False)

            try:
                self.on_recipe_select(self.root.ids.recipe_list.children[-1])
            except IndexError:
                pass

        elif list == "my_recipes":
            self.load_recipe_list_with_recipes(self.db.get_all_original_recipes(self.offset, self.page_size))

            if self.current_recipe.original_recipe:
                self.root.ids.screen_one.switch_on_delete_edit_btn(True)

            try:
                self.on_recipe_select(self.root.ids.recipe_list.children[-1])
            except IndexError:
                pass

        elif list == "favourites":
            self.load_recipe_list_with_recipes(self.db.get_all_favourite_recipes(self.offset, self.page_size))
            self.root.ids.screen_one.switch_on_delete_edit_btn(False)

            try:
                self.on_recipe_select(self.root.ids.recipe_list.children[-1])
            except IndexError:
                pass

        self.selected_recipe_list = list

    @staticmethod
    def get_recipe_extractor_data(response):
        recipe_data = []

        # for data in response:
        recipe_instructions = []
        # recipe_ingredients = []
        steps_count = 1

        for instruction in response["recipe"]["recipeInstructions"]:
            recipe_instructions.append(f"{steps_count}. {instruction['text']}\n")
            steps_count += 1

        image = response["recipe"]["image"][0]

        try:
            cook_t = response["recipe"]["cookTimeOriginalFormat"][2:-1]
        except KeyError:
            cook_t = "0"
        # print(image)

        recipe_info = {
            "recipe_api_id": None,
            "title": response["recipe"]["name"],
            "prep_time": response["recipe"]["prepTimeOriginalFormat"][2:-1],
            "cook_time": cook_t,
            "total_cook_time": response["recipe"]["totalTimeOriginalFormat"][2:-1],
            "servings": response["recipe"]["recipeYield"],
            "image_url": image,
            "favourite": False,
            "original_recipe": True,
            "instructions": " ".join(recipe_instructions),
            "cuisine": response["recipe"]["recipeCuisine"][0] if response["recipe"]["recipeCuisine"] else "",
            # recipe['cuisines'],
            "food_category": " ".join(response["recipe"]["recipeCategory"]),  # same thing as above
            "vegan": False,  # Diet information is not being provided by this API
            "vegetarian": False,
            "gluten_free": False,
            "dairy_free": False,
            "ingredients_data": response["recipe"]["recipeIngredients"],
        }

        recipe_data.append(recipe_info)

        return recipe_data

    @staticmethod
    def extract_information(response):
        recipes_data = []

        for recipe in response:
            recipe_instructions = []
            steps_count = 1

            for instructions in recipe["analyzedInstructions"]:
                if instructions["name"] != "":
                    recipe_instructions.append(f"{steps_count}. {instructions['name']}\n")
                    steps_count += 1

                for step in instructions["steps"]:
                    recipe_instructions.append(f"{steps_count}. {step['step']}\n")
                    steps_count += 1

            image = "assets/images/img.png"
            try:
                if recipe["image"] != '':
                    image = recipe["image"]
            except KeyError:
                pass

            recipe_info = {
                "recipe_api_id": recipe["id"],
                "title": recipe["title"],
                "prep_time": recipe["preparationMinutes"],
                "cook_time": recipe["cookingMinutes"],
                "total_cook_time": recipe["readyInMinutes"],
                "servings": recipe["servings"],
                "image_url": image,
                "favourite": False,
                "original_recipe": False,
                "instructions": " ".join(recipe_instructions),
                "cuisine": " ".join(recipe["cuisines"]),  # recipe['cuisines'],
                "food_category": " ".join(recipe["dishTypes"]),  # same thing as above
                "vegan": recipe["vegan"],
                "vegetarian": recipe["vegetarian"],
                "gluten_free": recipe["glutenFree"],
                "dairy_free": recipe["dairyFree"],
                "ingredients_data": recipe["extendedIngredients"],
            }

            recipes_data.append(recipe_info)

        return recipes_data

    def search_filtered_recipes_from_api(self, search_by, look_for, recipe_count):
        found_recipes = self.load_found_recipe(search_by, look_for, recipe_count)

        if found_recipes:
            return found_recipes

        self.show_show_more_btn(False)
        return

    def search_filtered_recipes_from_db(self, search_by, look_for, original, favs, strict):
        recipes = self.db.search_for_recipes(search_by, look_for, original, favs, strict)

        if recipes:
            return recipes
        return

    def get_search_criteria(self):
        search_by = []

        if self.search_selection:
            for criteria in self.search_selection:
                if criteria[2] is True:
                    search_by.append(criteria[0])
        else:
            search_by.append("title")
        return search_by

    def search_for_recipe(self, look_for):
        search_by = self.get_search_criteria()

        original = False
        favs = False
        strict = False

        if self.selected_recipe_list == "my_recipes":
            original = True
        elif self.selected_recipe_list == "favourites":
            favs = True
            strict = True

        recipes = self.search_filtered_recipes_from_db(search_by, look_for, original, favs, strict)

        if recipes:
            self.root.ids.recipe_list.clear_widgets()
            self.offset = 0
            self.load_recipe_list_with_recipes(recipes)
        else:
            self.root.ids.recipe_list.clear_widgets()
            self.offset = 0
            self.root.ids.recipe_scroll.scroll_y = 1

            if self.potentially_search_api:
                found_recipes = self.search_filtered_recipes_from_api(search_by, look_for, 3)

                if found_recipes:
                    self.load_recipe_list_with_recipes(found_recipes)
                    print("show btn still remains")
                    # self.show_show_more_btn(True)

    def add_or_remove_from_favourites(self):
        self.db.change_recipe_favourite_value(self.current_recipe)

        if not self.current_recipe.favourite:
            self.on_recipe_list_select(self.selected_recipe_list)

    def show_show_more_btn(self, show=False):
        if show:
            self.root.ids.show_more_btn.opacity = 1
            self.root.ids.show_more_btn.disable = False
        else:
            self.root.ids.show_more_btn.opacity = 0
            self.root.ids.show_more_btn.disable = True

    def show_more_btn_on_scroll(self, scroll_y):
        if scroll_y > 0.01:  # or not self.check_if_there_are_more_recipes_to_show():
            self.root.ids.show_more_btn.opacity = 0
            self.root.ids.show_more_btn.disable = True
            return

        elif scroll_y < 0.01:
            if not self.check_if_there_are_more_recipes_to_show() and self.selected_recipe_list != "all_recipes":
                return

            self.root.ids.show_more_btn.opacity = 1
            self.root.ids.show_more_btn.disable = False

    def check_if_there_are_more_recipes_to_show(self):
        recipes = False

        if self.selected_recipe_list == "all_recipes":
            recipes = self.db.get_recipes(self.offset, self.page_size)
        elif self.selected_recipe_list == "my_recipes":
            recipes = self.db.get_all_original_recipes(self.offset, self.page_size)
        elif self.selected_recipe_list == "favourites":
            recipes = self.db.get_all_favourite_recipes(self.offset, self.page_size)

        if recipes:
            return True

        return False

    def show_more_recipes(self):
        recipes_num = len(self.root.ids.recipe_list.children)

        self.on_recipe_list_select(self.selected_recipe_list)
        print(self.offset)

        self.root.ids.recipe_scroll.scroll_y = 1 - (1 / recipes_num * (recipes_num - 1.5))
        self.show_more_btn_on_scroll(self.root.ids.recipe_scroll.scroll_y)

    # Save new/edited recipe
    def done_creating_recipe(self):
        recipe_info = self.root.ids.screen_two.done_btn()

        if recipe_info:
            if self.db.get_original_recipe(recipe_info[1]):
                return

            self.db.add_recipe(*recipe_info)
            self.on_recipe_list_select(self.selected_recipe_list)
            self.root.ids.screen_two.cancel_add_edit_recipe()

    def delete_recipe(self):
        self.db.delete_recipe(self.current_recipe.title)  # , self.current_recipe.instructions)

        self.offset = 0

        self.root.ids.recipe_list.clear_widgets()
        self.load_recipe_list_with_recipes(self.db.get_all_original_recipes(self.offset, self.page_size))

        self.on_recipe_list_select(self.selected_recipe_list)

        try:
            self.on_recipe_select(self.root.ids.recipe_list.children[0])
        except IndexError:
            pass

    # Edit original recipe
    def edit_recipe(self):
        self.switch_screen()

        recipe = self.current_recipe

        recipe_data = [recipe.title, recipe.servings, recipe.prep_time,
                       recipe.cook_time, recipe.total_cook_time, recipe.instructions,
                       recipe.image_url, recipe.cuisine, recipe.food_category, recipe.vegan,
                       recipe.dairy_free, recipe.gluten_free, recipe.vegetarian, recipe.ingredients]

        self.root.ids.screen_two.show_edit_recipe_info(*recipe_data)
        self.root.ids.screen_two.ids.add_done_btn.on_release = lambda: self.done_editing(recipe)

    def done_editing(self, recipe):
        new_recipe_info = self.root.ids.screen_two.done_btn()
        print(new_recipe_info)
        self.db.edit_recipe(recipe, *new_recipe_info)
        self.root.ids.screen_two.cancel_add_edit_recipe()

        self.offset = 0

        self.root.ids.recipe_list.clear_widgets()
        self.load_recipe_list_with_recipes(self.db.get_all_original_recipes(self.offset, self.page_size))

        self.on_recipe_select(recipe)

    def switch_screen(self):
        self.root.ids.screens.transition = NoTransition()

        if self.root.ids.screens.current == "screen_one":
            self.root.ids.screen_one.switch_screen()
            self.root.ids.screen_two.ids.add_done_btn.on_release = self.done_creating_recipe
        else:
            self.root.ids.screen_two.switch_screen()

    def get_recipe_through_url(self, instance):
        print(self.url_window.content_cls.ids.window_input.text)
        url = self.url_window.content_cls.ids.window_input.text
        recipe = None
        recipes = []

        if url != "":
            print("EXTRACT")
            extracted_recipe = self.api_handler.extract_recipe_from_website(url)
            print(extracted_recipe)
            extracted_recipe_data = self.get_recipe_extractor_data(extracted_recipe)
            print(extracted_recipe_data)

            for rec in extracted_recipe_data:
                recipe = self.db.add_recipe(**rec)

                if recipe:
                    recipes.append(recipe)

            self.load_recipe_list_with_recipes(recipes)
            self.url_window.content_cls.ids.window_input.text = ""
            self.url_window.dismiss()
        else:
            return

    # Create the popup menu for recipe url input
    def show_url_window(self):
        if not self.url_window:
            self.url_window = MDDialog(
                title="Provide recipe URL",
                type="custom",
                content_cls=DialogContent(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=(0.65098, 0.35294, 0, 1),
                        on_release=lambda instance: self.close_url_window(instance),
                    ),
                    MDRaisedButton(
                        text="OK",
                        theme_text_color="Custom",
                        md_bg_color=(0.65098, 0.35294, 0, 1),
                        text_color=(0.9765, 0.9686, 0.8745, 1),
                        on_release=lambda instance: self.get_recipe_through_url(instance),
                    ), ],
                md_bg_color=(0.2392, 0.2196, 0.1725, 0.6),
            )

        self.url_window.open()

    # Create the popup window for email input
    def show_email_input_window(self):
        if not self.export_window:
            self.export_window = MDDialog(
                title="Provide recipient email address",
                type="custom",
                content_cls=DialogContent(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=(0.65098, 0.35294, 0, 1),
                        on_release=lambda instance: self.close_export_window(instance),
                    ),
                    MDRaisedButton(
                        text="OK",
                        theme_text_color="Custom",
                        md_bg_color=(0.65098, 0.35294, 0, 1),
                        text_color=(0.9765, 0.9686, 0.8745, 1),
                        on_release=lambda instance: self.write_an_email(instance),
                    ), ],
                md_bg_color=(0.2392, 0.2196, 0.1725, 0.6),
            )

        self.export_window.open()

    # Create the filter menu
    def show_search_by_options(self):
        if not self.search_menu:
            self.search_menu = MDDialog(
                title="Choose search method",
                type="confirmation",
                items=[
                    FilterItem(id="title_item", text="Title"),
                    FilterItem(id="ingredient_item", text="Ingredient"),
                    FilterItem(id="cuisine_item", text="Cuisine"),
                    FilterItem(id="food_cat_item", text="Category"),
                    FilterItem(id="vegan_item", text="Vegan"),
                    FilterItem(id="dairy_free_item", text="Dairy-free"),
                    FilterItem(id="gluten_free_item", text="Gluten-free"),
                    FilterItem(id="vegetarian_item", text="Vegetarian"),
                ],
                buttons=[
                    MDFlatButton(
                        id="cancel_btn",
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=(0.65098, 0.35294, 0, 1),
                        on_release=lambda instance: self.close_search_by_menu(instance),
                    ),
                    MDRaisedButton(
                        id="ok_btn",
                        text="OK",
                        theme_text_color="Custom",
                        md_bg_color=(0.65098, 0.35294, 0, 1),
                        text_color=(0.9765, 0.9686, 0.8745, 1),
                        on_release=lambda instance: self.ok_search_by_menu(instance),
                    ),
                ],
                md_bg_color=(0.2392, 0.2196, 0.1725, 0.6),
                on_touch_down=lambda instance, touch: self.check_touch_outside(instance, touch),
            )

            # Set searching by title to be a default
            self.search_menu.items[0].ids.check.active = True
            self.search_menu.items[0].ids.check.theme_text_color = "Custom"
            self.search_menu.items[0].ids.check.text_color = (0.65098, 0.35294, 0, 0.9)
            self.search_menu.items[0].state = "down"
            self.ok_search_by_menu(self.search_menu)

        self.search_menu.open()

    # Check if clicked outside the dialog
    def check_touch_outside(self, instance, touch):
        if instance.collide_point(*touch.pos):
            # Touch is inside the dialog, do nothing
            pass
        else:
            # Touch is outside the dialog, close the dialog
            self.close_search_by_menu(instance)

    # Closes the filter popup menu without saving the changes
    def close_search_by_menu(self, instance):

        for i in range(len(self.search_menu.items)):
            current_child_state = self.search_menu.items[i].state
            current_child_active = self.search_menu.items[i].ids.check.active

            if (current_child_state != self.search_selection[i][1] or
                    current_child_active != self.search_selection[i][2]):
                self.search_menu.items[i].state = self.search_selection[i][1]
                self.search_menu.items[i].ids.check.active = self.search_selection[i][2]

        self.search_menu.dismiss()

    # Closes the url popup window without saving the changes
    def close_url_window(self, instance):
        self.url_window.content_cls.ids.window_input.text = ""
        self.url_window.dismiss()

    # Closes the email popup window without saving the changes
    def close_export_window(self, instance):
        self.export_window.content_cls.ids.window_input.text = ""
        self.export_window.dismiss()

    # Closes the dialog and saves the changes
    def ok_search_by_menu(self, instance):
        self.search_selection = []

        if not list(filter(lambda x: x.ids.check.active is True, self.search_menu.items)):
            self.search_menu.items[0].ids.check.active = True
            self.search_menu.items[0].state = "down"

        for child in self.search_menu.items:
            if child.state == "normal" and child.ids.check.active is True:
                child.state = "down"
            elif child.state == "down" and child.ids.check.active is False:
                child.state = "normal"

            self.search_selection.append((child.text.lower(), child.state, child.ids.check.active))

        self.search_menu.dismiss()

    # Choose an image
    def show_image_chooser(self):
        file_chooser = FileChooserIconView()
        file_chooser.bind(on_submit=self.file_selected)

        popup = Popup(
            title="Select a Photo",
            content=file_chooser,
            size_hint=(None, None),
            size=(900, 700),
        )
        popup.open()

    def file_selected(self, instance, selection, touch):
        if selection:
            selected_file = selection[0]

            if selected_file[-4:] not in ("jpeg", ".jpg", ".png"):
                pass
            else:
                self.root.ids.screen_two.change_img(selected_file)

                # Close the file chooser popup
                instance.parent.parent.parent.dismiss()

    def export(self):
        recipe_data = self.root.ids.screen_one.export_recipe_data()

        desktop_path = os.path.join(os.path.expanduser("~"), 'Desktop')
        pdf_file_path = os.path.join(desktop_path, f"{str(recipe_data['title'].lower().replace(' ', '_'))}.pdf")

        # Set up PDF Canvas
        c = canvas.Canvas(pdf_file_path, pagesize=letter)
        width, height = letter

        # Define initial font size and line height
        font_size = 10
        line_height = 12

        # Function to wrap text into multiple lines based on specified line width
        def wrap_text(text, line_width):
            sentences = text.split("\n")
            lines = []
            for sentence in sentences:
                if sentence == "":
                    continue

                text = sentence.split()
                current_line = text[0]

                for word in text[1:]:
                    if c.stringWidth(current_line + ' ' + word, 'Helvetica', font_size) <= line_width - 40:
                        current_line += ' ' + word
                    else:
                        lines.append(current_line)
                        current_line = word

                lines.append(current_line)
            return lines

        # Write recipe details to PDF
        c.drawString(70, height - 80, f"Title: {recipe_data['title']}")

        info_text = f"Servings: {recipe_data['servings']} | Prep Time: {recipe_data['prep']} min | Cook Time: {recipe_data['cook_time']} min | Total Time: {recipe_data['total_cook_time']} min"
        c.drawString(70, height - 100, info_text)

        c.drawString(70, height - 120, "Ingredients:")
        for i, ingredient in enumerate(recipe_data['ingredients']):
            c.drawString(80, height - 140 - (i * line_height), f"{ingredient}")

        n = len(recipe_data['ingredients']) * line_height

        instructions_text = wrap_text(recipe_data['instructions'], width - 150)

        for i, line in enumerate(instructions_text):
            c.drawString(70, height - 140 - n - (i * line_height), line)

        # Save the PDF
        c.save()
        print(f"PDF exported to {pdf_file_path}")
