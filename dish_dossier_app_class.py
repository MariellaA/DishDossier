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
from kivymd.uix.selectioncontrol import MDCheckbox

from db_handler import DBHandler
from kivy.config import Config
from recipe_api_handler import RecipeAPIHandler

Config.set('graphics', 'resizable', False)

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.list import OneLineAvatarListItem, MDList, IRightBodyTouch, OneLineListItem, OneLineAvatarIconListItem
from recipe import Recipe


# Builder.load_file('layouts/main_layout.kv')


class RecipeList(MDList):
    pass


class RecipeCard(MDCard):
    def __init__(self, **kwargs):
        super(RecipeCard, self).__init__(**kwargs)
    #     self.orientation = 'horizontal'
    #     self.size_hint_y = None
    #     self.height = dp(100)
    #     self.spacing = dp(10)
    #
    #     self.image = AsyncImage(width=dp(100), size_hint_x=None, radius=24)
    #     # self.image.radius = 24
    #     # self.image.size_hint_x = None
    #     # self.image.size_hint_x = None
    #     self.title_button = MDFlatButton(text="",
    #                                      size_hint_x=None,
    #                                      width=dp(150),
    #                                      theme_text_color="Custom",
    #                                      text_color=(0.2392, 0.2196, 0.1725, 1),
    #                                      pos_hint={"center_x": 0.5, "center_y": 0.5},
    #                                      font_name="fonts/athiti/Athiti-SemiBold.ttf")
    #     self.title_button.bind(on_release=self.on_card_press)
    #
    #     self.add_widget(self.image)
    #     self.add_widget(self.title_button)
    #
    # def on_card_press(self, instance):
    #     # Implement the action you want when the card is pressed
    #     print(f"Recipe '{self.title_button.text}' pressed!")


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
        # print(self.manager)
        # self.manager.transition = NoTransition()
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
        # self.manager.transition = NoTransition()
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
            print(selected_file)
            self.ids.s2_recipe_image_display.source = selected_file
            self.ids.s2_recipe_image_display.reload()

            # Close the file chooser popup
            instance.parent.parent.parent.dismiss()

    # Delete image:
    def remove_image(self):
        self.ids.s2_recipe_image_display.source = ""
        self.ids.s2_recipe_image_display.reload()

    # Cancel editing or adding a recipe
    def cancel_add_edit_recipe(self):
        print(self.ids.add_cancel_btn.text)
        # print(self.ids)

        # Clear input data
        self.ids.s2_recipe_title_input.text = ""
        self.ids.s2_recipe_servings.text = ""
        self.ids.s2_recipe_prep_time.text = ""
        self.ids.s2_recipe_cook_time.text = ""
        self.ids.s2_recipe_total_time.text = ""
        self.ids.s2_recipe_instr.text = ""
        self.ids.s2_recipe_image_display.source = ""
        self.ids.vegan.active = False
        self.ids.dairy_free.active = False
        self.ids.gluten_free.active = False
        self.ids.vegetarian.active = False
        self.ids.s2_cuisine.text = ""
        self.ids.s2_category.text = ""
        # print(self.ids.s2_recipe_ingr.text.split('\n'))
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
        self.ids.s2_recipe_image_display.source = img
        self.ids.vegan.active = vegan
        self.ids.dairy_free.active = dairy_free
        self.ids.gluten_free.active = gluten_free
        self.ids.vegetarian.active = vegetarian
        self.ids.s2_cuisine.active = cuisine
        self.ids.s2_category.active = food_cat

        for ingredient in ingr:
            self.ids.s2_recipe_ingr.text += ingredient.ingredient + "\n"
        self.ids.s2_recipe_ingr.text = self.ids.s2_recipe_ingr.text[:-1]
        # self.ids.s2_recipe_ingr.text = ingr

    def done_btn(self):
        print(self.ids.add_done_btn.text)

        title = self.ids.s2_recipe_title_input.text
        servings = self.ids.s2_recipe_servings.text
        prep_t = self.ids.s2_recipe_prep_time.text
        cook_t = self.ids.s2_recipe_cook_time.text
        total_t = self.ids.s2_recipe_total_time.text
        vegan = self.ids.vegan.active
        dairy_free = self.ids.dairy_free.active
        gluten_free = self.ids.gluten_free.active
        vegetarian = self.ids.vegetarian.active
        cuisine = self.ids.s2_cuisine.text
        food_category = self.ids.s2_category.text
        instr = self.ids.s2_recipe_instr.text
        # instr = self.root.ids.screen_two.ids.s2_recipe_instr.text.split('\n')

        # print(instr)

        if self.ids.s2_recipe_image_display.source is not None:
            image = self.ids.s2_recipe_image_display.source
            print("IMMGGGG")
        else:
            image = "assets/images/img.png"
            print("NO IMMMGGG IMG")

        # print(self.ids.s2_recipe_ingr.text.split("\n"))
        ingr = self.ids.s2_recipe_ingr.text.split("\n")

        if title == "" or instr == "" or ingr == "" or (title == "" and instr == "" and ingr == ""):
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
        # self.model = DishDossierModel()
        self.db = DBHandler()

        self.selected_recipe_list = 'all_recipes'
        # self.load_random_recipe()
        # self.load_recipe_list_with_recipes()

        self.current_recipe = None
        # self.menu = None
        self.search_menu = None
        self.search_selection = []

        self.current_page = 0
        self.page_size = 6

    def build(self):
        Window.size = (1280, 720)
        self.theme_cls.theme_style = "Dark"
        # self.theme_cls.primary_palette = "Orange"
        self.theme_cls.primary_hue = "200"  # "500"
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style_switch_animation_duration = 0.8

        return Builder.load_file('layouts/main_layout.kv')

    def load_random_recipe(self):
        print('LOAD RECIPE FROM API')
        # self.load_recipe_list_with_recipes()
        recipes_data = self.api_handler.load_random_recipes_from_api()

        for recipe_info in recipes_data:
            print(recipe_info)

            recipe_exists = self.db.add_recipe(**recipe_info)
            # recipe_exists = self.db.add_recipe(**recipe_info, ingredients_data=ingredients_data)
            # recipe_id = self.db.add_recipe(recipe_api_id, title, prep_time, cook_time, total_cook_time, servings, image,
            #                                favourite,
            #                                original_recipe, instructions, ingredients_data)

            print(f"Recipe_ID: {recipe_exists}")

    def load_recipe_list_with_recipes(self, recipes):
        print('LOAD RECIPE FROM LIST')

        # recipes = self.db.get_all_recipes()
        print(f"ALL RECIPES:\n {recipes}")

        # self.root.ids.recipe_list.clear_widgets()

        if not recipes:
            print("No more recipes left.")
            self.root.ids.show_more_btn.opacity = 0
            self.root.ids.show_more_btn.disable = True
        else:
            # Display the recipes (customize this part based on your UI)
            for recipe in recipes:
                print(recipe)

                recipe_card = RecipeCard(id=str(recipe.recipe_api_id), )

                recipe_card.ids.recipe_img.source = recipe.image_url
                recipe_card.ids.recipe_title_btn.text = recipe.title
                recipe_card.bind(on_release=self.on_recipe_select)

                self.root.ids.recipe_list.add_widget(recipe_card)

            # Update the current page
            self.current_page += 1

        # for recipe in recipes:
        #     recipe_card = RecipeCard(id=str(recipe.recipe_api_id),)
        #
        #     recipe_card.ids.recipe_img.source = recipe.image_url
        #     recipe_card.ids.recipe_title_btn.text = recipe.title
        #     recipe_card.bind(on_release=self.on_recipe_select)
        #
        #     self.root.ids.recipe_list.add_widget(recipe_card)

    def on_recipe_select(self, instance):
        # print(self.root.ids.screen_one.ids)
        # print(instance.ids.recipe_title_btn.text)
        # print(type(instance.id))
        try:
            if instance.id != "None":
                # print("NOT NONE")
                recipe = self.db.get_recipe(instance.id)
            else:
                title = instance.ids.recipe_title_btn.text
                print("NONEEEE")
                recipe = self.db.get_original_recipe(title)
                # print(recipe)
        except AttributeError:
            print("ERRRRRROOOOR")
            recipe = instance
            # print(recipe.title)

        self.current_recipe = recipe

        if self.current_recipe.original_recipe:
            self.root.ids.screen_one.switch_on_delete_edit_btn(True)

        # print(f"TITLE: {recipe.title}")
        self.root.ids.screen_one.set_recipe_info(recipe)

    def on_recipe_list_select(self, list):
        if self.selected_recipe_list != list:
            self.root.ids.recipe_list.clear_widgets()
            self.current_page = 0
            self.root.ids.recipe_scroll.scroll_y = 1
            self.show_show_more_btn(self.root.ids.recipe_scroll.scroll_y)

        # Calculate the offset for pagination
        offset = self.current_page * self.page_size

        if list == "all_recipes":
            print("SELECT Sidebar")

            self.load_recipe_list_with_recipes(self.db.get_recipes(offset, self.page_size))
            self.root.ids.screen_one.switch_on_delete_edit_btn(False)

            try:
                self.on_recipe_select(self.root.ids.recipe_list.children[-1])
            except IndexError:
                pass
        elif list == "my_recipes":
            self.load_recipe_list_with_recipes(self.db.get_all_original_recipes(offset, self.page_size))

            if self.current_recipe.original_recipe:
                self.root.ids.screen_one.switch_on_delete_edit_btn(True)

        elif list == "favourites":
            print("SELECT Sidebar")
            self.load_recipe_list_with_recipes(self.db.get_all_favourite_recipes(offset, self.page_size))
            self.root.ids.screen_one.switch_on_delete_edit_btn(False)

            try:
                self.on_recipe_select(self.root.ids.recipe_list.children[-1])
            except IndexError:
                pass

        self.selected_recipe_list = list

    def search_for_recipe(self, look_for):
        print(f"Searched str: {look_for}")

        self.root.ids.search_text.text = ""
        print(f"CURRENT LIST: {self.selected_recipe_list}")

        search_by = []

        if self.search_selection:
            for criteria in self.search_selection:
                if criteria[2] is True:
                    print(criteria[0])
                    search_by.append(criteria[0])
        else:
            print("NONEEE")
            search_by.append("title")

        original = False
        favs = False

        if self.selected_recipe_list == "my_recipes":
            original = True
        elif self.selected_recipe_list == "favourites":
            favs = True

        recipes = self.db.search_for_recipes(search_by, look_for, original, favs)

        self.root.ids.recipe_list.clear_widgets()
        self.load_recipe_list_with_recipes(recipes)
        self.root.ids.recipe_scroll.scroll_y = 1

    def add_or_remove_from_favourites(self):
        self.db.change_recipe_favourite_value(self.current_recipe)

        if not self.current_recipe.favourite:
            self.on_recipe_list_select(self.selected_recipe_list)

    def show_show_more_btn(self, scroll_y):
        # print(scroll_y)
        if scroll_y > 0.01 or not self.check_if_there_are_more_recipes_to_show():
            self.root.ids.show_more_btn.opacity = 0
            self.root.ids.show_more_btn.disable = True
            return

        elif scroll_y < 0.01:
            self.root.ids.show_more_btn.opacity = 1
            self.root.ids.show_more_btn.disable = False

        # elif scroll_y > 0.01:
        #     self.root.ids.show_more_btn.opacity = 0
        #     self.root.ids.show_more_btn.disable = True

    def check_if_there_are_more_recipes_to_show(self):
        offset = self.current_page * self.page_size
        recipes = False

        if self.selected_recipe_list == "all_recipes":
            recipes = self.db.get_recipes(offset, self.page_size)
        elif self.selected_recipe_list == "my_recipes":
            recipes = self.db.get_all_original_recipes(offset, self.page_size)
        elif self.selected_recipe_list == "favourites":
            recipes = self.db.get_all_favourite_recipes(offset, self.page_size)

        if recipes:
            return True

        # print(f"CHECKING {True if recipes else False}")
        return False

    def show_more_recipes(self):
        print("show more")
        recipes_num = len(self.root.ids.recipe_list.children)

        self.on_recipe_list_select(self.selected_recipe_list)
        print(len(self.root.ids.recipe_list.children))

        # print(1 - (1 / recipes_num * (len(self.root.ids.recipe_list.children) - 2)))
        self.root.ids.recipe_scroll.scroll_y = 1 - (1 / recipes_num * (recipes_num - 1.5))
        self.show_show_more_btn(self.root.ids.recipe_scroll.scroll_y)

    # Save new/edited recipe
    def done_creating_recipe(self):
        recipe_info = self.root.ids.screen_two.done_btn()
        print(f"DONE RECIPE CREATING {recipe_info}")

        if recipe_info:
            self.db.add_recipe(*recipe_info)
            self.on_recipe_list_select(self.selected_recipe_list)
            self.root.ids.screen_two.cancel_add_edit_recipe()

    def delete_recipe(self):
        print("DEEEEEELEEEETEEEE")
        print(self.current_recipe.instructions)
        self.db.delete_recipe(self.current_recipe.title, self.current_recipe.instructions)
        self.on_recipe_list_select(self.selected_recipe_list)

    # Edit original recipe
    def edit_recipe(self):
        print("EDIIIIIIIIIIIIIIIT")
        # print(self.current_recipe.recipe_api_id)
        # print(self.current_recipe.recipe_id)
        # print(self.current_recipe.instructions)
        # print(self.current_recipe)
        self.switch_screen()
        recipe = self.current_recipe

        recipe_data = [recipe.title, recipe.servings, recipe.prep_time,
                       recipe.cook_time, recipe.total_cook_time, recipe.instructions,
                       recipe.image_url, recipe.cuisine, recipe.food_category, recipe.vegan,
                       recipe.dairy_free, recipe.gluten_free, recipe.vegetarian, recipe.ingredients]
        # print(recipe_data)
        self.root.ids.screen_two.show_edit_recipe_info(*recipe_data)
        print(f"DONE EDITIIIING {recipe}")
        self.root.ids.screen_two.ids.add_done_btn.on_release = lambda: self.done_editing(recipe)

    def done_editing(self, recipe):
        print("DHSHSHZHRSHSH")
        # print(self.current_recipe.title)
        print(recipe.title)
        print("CURR RECIPE")
        # print(self.current_recipe.instructions)
        print(recipe.instructions)
        new_recipe_info = self.root.ids.screen_two.done_btn()
        # print(new_recipe_info)
        print("NEW INFOOOOOO")
        print(*new_recipe_info)
        self.db.edit_recipe(recipe, *new_recipe_info)
        print(recipe.instructions)
        self.root.ids.screen_two.cancel_add_edit_recipe()
        self.on_recipe_list_select(self.selected_recipe_list)
        self.on_recipe_select(recipe)

    def switch_screen(self):
        self.root.ids.screens.transition = NoTransition()

        if self.root.ids.screens.current == "screen_one":
            self.root.ids.screen_one.switch_screen()
            self.root.ids.screen_two.ids.add_done_btn.on_release = self.done_creating_recipe
        else:
            self.root.ids.screen_two.switch_screen()
        print(self.root.ids.screens.current)

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
                # print("CLOSE")
                # print(current_child_state)
                # print(current_child_active)

            # print("CLOSE")
            # print("---------------------------")
            # print(self.dialog.items[i].state)
            # print(self.dialog.items[i].ids.check.active)

        self.search_menu.dismiss()

    # Closes the dialog and saves the changes
    def ok_search_by_menu(self, instance):
        self.search_selection = []

        if not list(filter(lambda x: x.ids.check.active is True, self.search_menu.items)):
            # print("NOt ONE TRUE")
            self.search_menu.items[0].ids.check.active = True
            self.search_menu.items[0].state = "down"
            # return

        for child in self.search_menu.items:
            # print("OKOKOKOK")
            # print(child.state)
            # print(child.ids.check.active)
            if child.state == "normal" and child.ids.check.active is True:
                child.state = "down"
            elif child.state == "down" and child.ids.check.active is False:
                child.state = "normal"

            # print("---------------------------")
            # print(child.state)
            # print(child.ids.check.active)
            self.search_selection.append((child.text.lower(), child.state, child.ids.check.active))
            # print(self.dialog_selection)
        self.search_menu.dismiss()

    def toggle_button_callback(self, instance):
        # instance.selected = not instance.selected
        print(instance.ids)
        print("cheeck")
        print("SHIIIIIIIIIT")
        self.search_menu.dismiss()

    # def filter_callback(self, criterion, active):
    #     if active:
    #         print(f"Selected criterion: {criterion}")
    #     else:
    #         print(f"Unselected criterion: {criterion}")

    # def hide_filter_menu(self, instance):
    #     # Called when the dropdown menu is dismissed
    #     print("HIDE")

    # def _build_recipe_list(self):
    #     # Build the left column for the list of recipes
    #     for recipe in self.model.recipes:
    #         item = OneLineAvatarListItem(text=recipe['title'])
    #         item.add_widget(Image(source=recipe['image']))
    #         item.bind(on_release=self.on_recipe_select)
    #         self.recipe_list.add_widget(item)
    #
    #     self.add_widget(self.recipe_list)

    # def switch_theme_style(self):
    #     self.theme_cls.primary_palette = (
    #         "Orange" if self.theme_cls.primary_palette == "Red" else "Red"
    #     )
    #     self.theme_cls.theme_style = (
    #         "Dark" if self.theme_cls.theme_style == "Light" else "Light"
    #     )
    # self.text_color = ("#252526" if self.theme_cls.theme_style == "Light" else "#ebebeb")
