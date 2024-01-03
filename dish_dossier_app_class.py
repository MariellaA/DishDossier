import kivy
import sqlite3 as sq
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import NoTransition
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from db_handler import DBHandler
from kivy.config import Config
from recipe_api_handler import RecipeAPIHandler

Config.set('graphics', 'resizable', False)
Config.set('kivy', 'window_icon', 'assets/images/start_logo.png')

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.list import OneLineAvatarListItem, MDList, IRightBodyTouch, OneLineListItem, OneLineAvatarIconListItem


class RecipeList(MDList):
    pass


class RecipeCard(MDCard):
    def __init__(self, **kwargs):
        super(RecipeCard, self).__init__(**kwargs)


class RecipeItem(OneLineAvatarListItem):
    pass


class ScreenOne(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenOne, self).__init__(**kwargs)

    def switch_on_delete_edit_btn(self, on_off):
        if on_off is False:
            self.ids.delete_btn.disabled = True
            self.ids.edit_btn.disabled = True

            self.ids.delete_btn.opacity = 0
            self.ids.edit_btn.opacity = 0
        elif on_off is True:
            self.ids.edit_btn.opacity = 1
            self.ids.delete_btn.opacity = 1

            self.ids.edit_btn.disabled = False
            self.ids.delete_btn.disabled = False

    def switch_screen(self):
        self.manager.current = 'screen_two'

    def set_recipe_info(self, recipe):
        self.ids.recipe_title.text = recipe.title.upper()
        self.ids.recipe_prep_time.text = str(recipe.prep_time) if recipe.prep_time != -1 else 'n/a'
        self.ids.recipe_cook_time.text = str(recipe.cook_time) if recipe.cook_time != -1 else 'n/a'
        self.ids.recipe_total_time.text = str(recipe.total_cook_time) if recipe.total_cook_time != -1 else 'n/a'
        self.ids.recipe_servings.text = str(recipe.servings) if recipe.servings != -1 else 'N/A'
        self.ids.vegan.text_color = (0.15, 0.5, 0.12, 1) if recipe.vegan else (0.1176, 0.1176, 0.1176, 0.2)
        self.ids.dairy_free.text_color = (0.2392, 0.2196, 0.8, 1) if recipe.dairy_free else (
            0.1176, 0.1176, 0.1176, 0.2)
        self.ids.gluten_free.text_color = (0.5, 0.3, 0.1, 1) if recipe.gluten_free else (0.1176, 0.1176, 0.1176, 0.2)
        self.ids.vegetarian.text_color = (0.4, 0.6, 0, 1) if recipe.vegetarian else (0.1176, 0.1176, 0.1176, 0.2)
        self.ids.recipe_instr.text = recipe.instructions

        # Set Recipe Image and Ingredients
        self.ids.recipe_full_image.source = recipe.image_url if recipe.image_url else 'assets/images/img.png'

        # Set Image button and label
        if recipe.favourite:
            self.ids.favs_button.icon = "heart"
            self.ids.favs_label.text = "Added to Favourites"
        else:
            self.ids.favs_button.icon = "heart-outline"
            self.ids.favs_label.text = "Add to Favourites"

        res = ""
        for ingredient in recipe.ingredients:
            res += f"{ingredient.ingredient}\n"
        self.ids.recipe_ingr.text = res


class ScreenTwo(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenTwo, self).__init__(**kwargs)

    def switch_screen(self):
        self.manager.current = 'screen_one'

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
        # print(instance.ids)
        if selection:
            selected_file = selection[0]
            self.ids.s2_recipe_image_display.source = selected_file
            self.ids.s2_recipe_image_display.reload()

            # Close the file chooser popup
            instance.parent.parent.parent.dismiss()

    # Delete image:
    def remove_image(self):
        self.ids.s2_recipe_image_display.source = "assets/images/img.png"
        self.ids.s2_recipe_image_display.reload()

    # Cancel editing or adding a recipe
    def cancel_add_edit_recipe(self):
        # Clear input data
        self.ids.s2_recipe_title_input.text = ""
        self.ids.s2_recipe_servings.text = ""
        self.ids.s2_recipe_prep_time.text = ""
        self.ids.s2_recipe_cook_time.text = ""
        self.ids.s2_recipe_total_time.text = ""
        self.ids.s2_recipe_instr.text = ""
        self.ids.s2_recipe_image_display.source = "assets/images/img.png"
        self.ids.vegan.active = False
        self.ids.dairy_free.active = False
        self.ids.gluten_free.active = False
        self.ids.vegetarian.active = False
        self.ids.s2_cuisine.text = ""
        self.ids.s2_category.text = ""
        self.ids.s2_recipe_ingr.text = ""

        self.switch_screen()

    def show_edit_recipe_info(self, title, servings, prep_t, cook_t, total_t, instr, img, cuisine, food_cat, vegan,
                              dairy_free, gluten_free, vegetarian, ingr):
        self.ids.s2_recipe_title_input.text = title
        self.ids.s2_recipe_servings.text = str(servings) if servings != -1 else ""
        self.ids.s2_recipe_prep_time.text = str(prep_t) if prep_t != -1 else ""
        self.ids.s2_recipe_cook_time.text = str(cook_t) if cook_t != -1 else ""
        self.ids.s2_recipe_total_time.text = str(total_t) if total_t != -1 else ""
        self.ids.s2_recipe_instr.text = instr
        self.ids.s2_recipe_image_display.source = img if img != "" else "assets/images/img.png"
        self.ids.vegan.active = vegan
        self.ids.dairy_free.active = dairy_free
        self.ids.gluten_free.active = gluten_free
        self.ids.vegetarian.active = vegetarian
        self.ids.s2_cuisine.active = cuisine
        self.ids.s2_category.active = food_cat

        for ingredient in ingr:
            self.ids.s2_recipe_ingr.text += ingredient.ingredient + "\n"
        self.ids.s2_recipe_ingr.text = self.ids.s2_recipe_ingr.text[:-1]

    def done_btn(self):
        title = self.ids.s2_recipe_title_input.text
        servings = self.ids.s2_recipe_servings.text
        prep_t = self.ids.s2_recipe_prep_time.text if self.ids.s2_recipe_prep_time.text != "" else 0
        cook_t = self.ids.s2_recipe_cook_time.text if self.ids.s2_recipe_cook_time.text != "" else 0
        total_t = self.ids.s2_recipe_total_time.text if self.ids.s2_recipe_total_time.text != "" else 0
        vegan = self.ids.vegan.active
        dairy_free = self.ids.dairy_free.active
        gluten_free = self.ids.gluten_free.active
        vegetarian = self.ids.vegetarian.active
        cuisine = self.ids.s2_cuisine.text
        food_category = self.ids.s2_category.text
        instr = self.ids.s2_recipe_instr.text

        if self.ids.s2_recipe_image_display.source is not None:
            image = self.ids.s2_recipe_image_display.source
        else:
            image = "assets/images/img.png"

        ingr = self.ids.s2_recipe_ingr.text.split("\n")

        if title == "" or instr == "" or ingr == [''] or (title == "" and instr == "" and ingr == ""):
            return

        return None, title, prep_t, cook_t, total_t, servings, image, False, True, instr, cuisine, food_category, vegan, vegetarian, gluten_free, dairy_free, ingr


class FilterItem(OneLineAvatarIconListItem):
    divider = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected = False
        self.theme_text_color = "Custom"
        self.text_color = (0.1176, 0.1176, 0.1176, 1)
        self.bg_color = (0.9725, 0.902, 0.7333, 1)

    def set_icon(self, instance_check):
        if not instance_check.active:
            instance_check.active = True  # False if instance_check.active else True
        else:
            instance_check.active = False


class DishDossierController(BoxLayout):
    pass


class DishDossierApp(MDApp):
    def __init__(self):
        super().__init__()
        self.api_handler = RecipeAPIHandler()
        self.db = DBHandler()

        self.selected_recipe_list = 'all_recipes'
        # self.load_random_recipe()
        # self.load_recipe_list_with_recipes()

        self.current_recipe = None
        self.search_menu = None
        self.potentially_search_api = False
        self.search_selection = []

        self.offset = 0
        self.page_size = 6

    def build(self):
        Window.size = (1280, 720)
        self.theme_cls.theme_style = "Dark"
        # self.theme_cls.primary_palette = "Orange"
        self.theme_cls.primary_hue = "200"  # "500"
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style_switch_animation_duration = 0.8

        return Builder.load_file('layouts/main_layout.kv')

    def load_random_recipe(self, recipe_count):
        recipes_data = self.api_handler.load_random_recipes_from_api(recipe_count)

        for recipe_info in recipes_data:
            recipe_exists = self.db.add_recipe(**recipe_info)

            print(f"Recipe_ID: {recipe_exists}")

    def load_found_recipe(self, search_by, look_for, recipe_count):
        found_recipes = self.api_handler.find_recipe_from_api(search_by, look_for, recipe_count)
        recipes = []

        for recipe_info in found_recipes:
            recipe_exists = self.db.add_recipe(**recipe_info)
            recipes.append(recipe_exists)

        return recipes

    def load_recipe_list_with_recipes(self, recipes):
        if not recipes:
            self.root.ids.show_more_btn.opacity = 0
            self.root.ids.show_more_btn.disable = True
        else:
            # Display the recipes (customize this part based on your UI)
            for recipe in recipes:
                recipe_card = RecipeCard(id=str(recipe.recipe_api_id), )

                recipe_card.ids.recipe_img.source = recipe.image_url
                recipe_card.ids.recipe_title_btn.text = recipe.title
                recipe_card.bind(on_release=self.on_recipe_select)

                self.root.ids.recipe_list.add_widget(recipe_card)

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

    def on_recipe_list_select(self, list):
        if self.selected_recipe_list != list:
            self.root.ids.recipe_list.clear_widgets()
            self.offset = 0
            self.potentially_search_api = False
            self.root.ids.recipe_scroll.scroll_y = 1
            self.show_show_more_btn(self.root.ids.recipe_scroll.scroll_y)

        if list == "all_recipes":

            if not self.check_if_there_are_more_recipes_to_show():
                self.load_random_recipe(6)

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

        elif list == "favourites":
            self.load_recipe_list_with_recipes(self.db.get_all_favourite_recipes(self.offset, self.page_size))
            self.root.ids.screen_one.switch_on_delete_edit_btn(False)

            try:
                self.on_recipe_select(self.root.ids.recipe_list.children[-1])
            except IndexError:
                pass

        self.selected_recipe_list = list

    def search_for_recipe(self, look_for):

        self.root.ids.search_text.text = ""

        search_by = []

        if self.search_selection:
            for criteria in self.search_selection:
                if criteria[2] is True:
                    search_by.append(criteria[0])
        else:
            search_by.append("title")

        original = False
        favs = False

        if self.selected_recipe_list == "my_recipes":
            original = True
        elif self.selected_recipe_list == "favourites":
            favs = True
        elif self.selected_recipe_list == "all_recipes":
            self.potentially_search_api = True

        recipes = self.db.search_for_recipes(search_by, look_for, original, favs)

        if recipes:
            self.root.ids.recipe_list.clear_widgets()
            self.load_recipe_list_with_recipes(recipes)
        else:
            self.root.ids.recipe_list.clear_widgets()

            if self.potentially_search_api:
                found_recipes = self.load_found_recipe(search_by, look_for, 1)

                if found_recipes:
                    self.load_recipe_list_with_recipes(found_recipes)

        self.root.ids.recipe_scroll.scroll_y = 1

    def add_or_remove_from_favourites(self):
        self.db.change_recipe_favourite_value(self.current_recipe)

        if not self.current_recipe.favourite:
            self.on_recipe_list_select(self.selected_recipe_list)

    def show_show_more_btn(self, scroll_y):
        if scroll_y > 0.01:  # or not self.check_if_there_are_more_recipes_to_show():
            self.root.ids.show_more_btn.opacity = 0
            self.root.ids.show_more_btn.disable = True
            return

        elif scroll_y < 0.01:
            # print("SCROOOL")
            if not self.check_if_there_are_more_recipes_to_show() and self.selected_recipe_list != "all_recipes":
                # if there are no more recipes - load 6 new random from api
                print("No more recipes. Load more")
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
        self.show_show_more_btn(self.root.ids.recipe_scroll.scroll_y)

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
        self.db.delete_recipe(self.current_recipe.title, self.current_recipe.instructions)

        self.offset = 0

        self.root.ids.recipe_list.clear_widgets()
        self.load_recipe_list_with_recipes(self.db.get_all_original_recipes(self.offset, self.page_size))

        self.on_recipe_list_select(self.selected_recipe_list)

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

    # Closes the dialog without saving the changes
    def close_search_by_menu(self, instance):

        for i in range(len(self.search_menu.items)):
            current_child_state = self.search_menu.items[i].state
            current_child_active = self.search_menu.items[i].ids.check.active

            if (current_child_state != self.search_selection[i][1] or
                    current_child_active != self.search_selection[i][2]):
                self.search_menu.items[i].state = self.search_selection[i][1]
                self.search_menu.items[i].ids.check.active = self.search_selection[i][2]

        self.search_menu.dismiss()

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

    def toggle_button_callback(self, instance):
        self.search_menu.dismiss()
