from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.list import OneLineAvatarIconListItem, MDList
from kivymd.uix.screen import MDScreen


class RecipeList(MDList):
    pass


class DialogContent(MDBoxLayout):
    name = StringProperty()

    def __init__(self, **kwargs):
        super(DialogContent, self).__init__(**kwargs)


class RecipeCard(MDCard):
    def __init__(self, **kwargs):
        super(RecipeCard, self).__init__(**kwargs)


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
        self.ids.recipe_full_image.source = recipe.image_url if recipe.image_url else 'images/img.png'

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

    def export_recipe_data(self):
        recipe_data = {
            "title": self.ids.recipe_title.text.lower(),
            "servings": self.ids.recipe_servings.text,
            "prep": self.ids.recipe_prep_time.text,
            "cook_time": self.ids.recipe_cook_time.text,
            "total_cook_time": self.ids.recipe_total_time.text,
            "ingredients": self.ids.recipe_ingr.text.split("\n"),
            "instructions": self.ids.recipe_instr.text,
        }

        return recipe_data


class ScreenTwo(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenTwo, self).__init__(**kwargs)

    def switch_screen(self):
        self.manager.current = 'screen_one'

    def change_img(self, image):
        self.ids.s2_recipe_image_display.source = image
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
        self.ids.s2_recipe_image_display.source = "images/img.png"
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
        self.ids.s2_recipe_image_display.source = img if img != "" else "images/img.png"
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
            image = "images/img.png"

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
