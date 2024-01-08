import os

from sqlalchemy import create_engine, or_, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from models import Base, Recipe, Ingredient, recipes_ingredients


class DBHandler:
    def __init__(self):
        self._path = "sqlite:///" + os.path.join(os.path.dirname(os.path.abspath(__file__)), "dish_dossier_db.db")
        self.engine = create_engine(self._path)  # , echo=True)
        self.create_tables()
        self.session = sessionmaker(bind=self.engine)()

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    def add_recipe(self, recipe_api_id, title, prep_time, cook_time, total_cook_time,
                   servings, image_url, favourite, original_recipe, instructions, cuisine,
                   food_category, vegan, vegetarian, gluten_free, dairy_free, ingredients_data):
        # try:
        print(recipe_api_id)
        existing_recipe = self.get_recipe(
                recipe_api_id)

        #existing_original_recipe = self.get_original_recipe(title)

        print(title)
        try:
            print(existing_recipe.title)
            # print(existing_original_recipe.title)
        except AttributeError:
            pass

        if not existing_recipe or original_recipe:
            # Create a Recipe object
            recipe = Recipe(
                title=title,
                recipe_api_id=recipe_api_id,
                prep_time=prep_time,
                cook_time=cook_time,
                total_cook_time=total_cook_time,
                servings=servings,
                image_url=image_url,
                favourite=favourite,
                original_recipe=original_recipe,
                instructions=instructions,
                cuisine=cuisine,
                food_category=food_category,
                vegan=vegan,
                vegetarian=vegetarian,
                gluten_free=gluten_free,
                dairy_free=dairy_free,
            )

            print(recipe.title)
            # Add the Recipe to the database
            self.session.add(recipe)
            print("ADDING TO DB")

            # Check for existing ingredients and add only new ones
            for ingredient_info in ingredients_data:
                try:
                    ingredient = self.find_ingredient(original_recipe, ingredient_info)

                    if not ingredient:
                        ingredient = self.create_ingredient(original_recipe, ingredient_info)
                        self.session.add(ingredient)

                    recipe.ingredients.append(ingredient)
                    self.session.commit()

                except IntegrityError:
                    # Handle integrity error (duplicate API ID for ingredients)
                    print("ingr rollback")
                    self.session.rollback()

            return recipe  # Return the added recipe

        # except IntegrityError:
        #     # Handle integrity error (duplicate API ID for recipes)
        #     print("recipe rollback")
        #     self.session.rollback()
        #     existing_recipe = self.get_recipe(
        #         recipe_api_id)  # self.session.query(Recipe).filter_by(recipe_api_id=recipe_api_id).first()
        #
        #     if existing_recipe:
        #         print(f"Recipe with recipe_api_id {recipe_api_id} already exists.")
        #         return  #existing_recipe  # Return existing recipe instead of adding a new one

    def create_ingredient(self, original, ingredient_info):
        if not original:
            ingredient = Ingredient(
                ingredient_api_id=ingredient_info['id'],
                ingredient=ingredient_info['originalString'] if 'originalString' in ingredient_info else
                ingredient_info['original']
            )
        else:
            ingredient = Ingredient(
                ingredient_api_id=None,
                ingredient=ingredient_info
            )

        if ingredient:
            return ingredient
        return

    def find_ingredient(self, original, ingredient_info):
        if not original:
            ingredient_api_id = ingredient_info['id']
            ingredient = (
                self.session.query(Ingredient)
                .filter_by(ingredient_api_id=ingredient_api_id)
                .first()
            )
        else:
            ingredient = (
                self.session.query(Ingredient).filter_by(ingredient=ingredient_info).first()
            )

        if ingredient:
            return ingredient

        return

    def get_recipes(self, offset, page_size):
        recipes = self.session.query(Recipe).filter_by(original_recipe=False, ).offset(offset).limit(page_size).all()
        return recipes

    def get_all_favourite_recipes(self, offset, page_size):
        recipes = self.session.query(Recipe).filter_by(favourite=True, ).offset(offset).limit(page_size).all()
        return recipes

    def get_all_original_recipes(self, offset, page_size):
        recipes = self.session.query(Recipe).filter_by(original_recipe=True, ).offset(offset).limit(page_size).all()
        return recipes

    def search_for_recipes(self, criteria, search_text, original, favs, strict):
        # Build the dynamic OR/AND clauses for each criterion
        or_clauses = []
        and_clauses = []

        for criterion in criteria:
            if criterion == "title":
                and_clauses.append(Recipe.title.ilike(f'%{search_text}%'))
            elif criterion == "ingredient":
                and_clauses.append(Ingredient.ingredient.ilike(f'%{search_text}%'))
            elif criterion == "cuisine":
                and_clauses.append(Recipe.cuisine.ilike(f'%{search_text}%'))
            elif criterion == "category":
                and_clauses.append(Recipe.food_category.ilike(f'%{search_text}%'))
            elif criterion == "vegan":
                and_clauses.append(Recipe.vegan)
            elif criterion == "dairy-free":
                and_clauses.append(Recipe.dairy_free)
            elif criterion == "gluten-free":
                and_clauses.append(Recipe.gluten_free)
            elif criterion == "vegetarian":
                and_clauses.append(Recipe.vegetarian)

        if original:
            and_clauses.append(Recipe.original_recipe)
        elif favs:
            if strict:
                and_clauses.append(Recipe.favourite)
            else:
                or_clauses.append(Recipe.favourite)

        # Combine the OR clauses with an AND clause
        or_combined_conditions = or_(*or_clauses)
        and_combined_conditions = and_(*and_clauses)
        final_combined_condition = and_(or_combined_conditions, and_combined_conditions)

        # Apply the dynamic clause to the base query
        recipes = (
            self.session.query(Recipe)
            .outerjoin(recipes_ingredients, Recipe.recipe_id == recipes_ingredients.c.recipe_id)
            .outerjoin(Ingredient, recipes_ingredients.c.ingredient_id == Ingredient.ingredient_id)
            .filter(final_combined_condition)
            .all()
        )

        return recipes

    # Get the selected recipe from the recipe list
    def get_recipe(self, iid):
        recipe = self.session.query(Recipe).filter_by(recipe_api_id=iid, ).limit(1).first()
        return recipe

    # Get the original recipe selected from the recipe list
    def get_original_recipe(self, title):
        recipe = self.session.query(Recipe).filter_by(original_recipe=True, title=title).limit(1).first()
        return recipe

    def change_recipe_favourite_value(self, recipe):
        recipe.favourite = True if recipe.favourite is False else False
        self.session.commit()

    # Delete an original recipe
    def delete_recipe(self, title):
        # Retrieve the recipe with the specified title
        recipe = self.get_original_recipe(title)

        if recipe:
            # Delete the recipe itself
            self.session.delete(recipe)
            self.session.commit()
            print(f"Recipe with title '{title}' and associated ingredients deleted successfully.")
        else:
            print(f"No recipe found with title '{title}'.")

    # Edit recipe information
    def edit_recipe(self, recipe, r_id, title, prep_t, cook_t, total_t, servings, image, fav, original, instr, cuisine,
                    food_category, vegan, vegetarian, gluten_free, dairy_free, ingr):
        recipe.title = title
        recipe.prep_time = prep_t
        recipe.cook_time = cook_t
        recipe.total_cook_time = total_t
        recipe.servings = servings
        recipe.image_url = image
        recipe.cuisine = cuisine
        recipe.food_category = food_category
        recipe.vegan = vegan
        recipe.dairy_free = dairy_free
        recipe.gluten_free = gluten_free
        recipe.vegetarian = vegetarian
        recipe.instructions = instr

        new_ingredients = []
        for ingredient_name in ingr:
            ingredient = self.find_ingredient(True,
                                              ingredient_name)  # self.session.query(Ingredient).filter_by(ingredient=ingredient_name).first()

            if not ingredient:
                ingredient = self.create_ingredient(True, ingredient_name)  # Ingredient(ingredient=ingredient_name)

            new_ingredients.append(ingredient)

        recipe.ingredients = new_ingredients

        self.session.commit()
