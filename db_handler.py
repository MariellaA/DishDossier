import os

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, Boolean, Text, or_, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, aliased
import sqlite3 as sq

Base = declarative_base()

recipes_ingredients = Table(
    'recipes_ingredients',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.recipe_id')),
    Column('ingredient_id', Integer, ForeignKey('ingredients.ingredient_id'))
)


class Recipe(Base):
    __tablename__ = 'recipes'
    recipe_id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_api_id = Column(Integer, unique=True)
    title = Column(String, nullable=False)
    prep_time = Column(Integer)
    cook_time = Column(Integer)
    total_cook_time = Column(Integer)
    servings = Column(Integer)
    image_url = Column(String)
    favourite = Column(Boolean, default=False)
    original_recipe = Column(Boolean, default=False)
    instructions = Column(Text)
    cuisine = Column(Text)
    food_category = Column(Text)
    vegan = Column(Boolean, default=False)
    vegetarian = Column(Boolean, default=False)
    gluten_free = Column(Boolean, default=False)
    dairy_free = Column(Boolean, default=False)
    ingredients = relationship('Ingredient', secondary=recipes_ingredients, cascade='all')


class Ingredient(Base):
    __tablename__ = 'ingredients'
    ingredient_id = Column(Integer, primary_key=True, autoincrement=True)
    ingredient_api_id = Column(Integer, unique=True, nullable=True)
    ingredient = Column(String)


class DBHandler:
    def __init__(self):
        self._path = "sqlite:///" + os.path.join(os.path.dirname(os.path.abspath(__file__)), "dish_dossier_db.db")
        # print(self._path)
        self.engine = create_engine(self._path, echo=True)
        self.create_tables()
        self.session = sessionmaker(bind=self.engine)()

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    # def get_page_recipes(self, offset, page_size):
    #     # Query the database for the next batch of recipes
    #     recipes = self.session.query(Recipe).offset(offset).limit(page_size).all()
    #
    #     return recipes

    def add_recipe(self, recipe_api_id, title, prep_time, cook_time, total_cook_time,
                   servings, image_url, favourite, original_recipe, instructions, cuisine,
                   food_category, vegan, vegetarian, gluten_free, dairy_free, ingredients_data):
        try:
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

            # Add the Recipe to the database
            self.session.add(recipe)
            # self.session.commit()
            print("ADDING TO DB")
            print(ingredients_data)

            # Check for existing ingredients and add only new ones
            for ingredient_info in ingredients_data:
                print(f"DB ADDING RECIPE INGR {ingredient_info}")
                try:
                    if not original_recipe:
                        print("Not original")
                        ingredient_api_id = ingredient_info['id']
                        ingredient = (
                            self.session.query(Ingredient)
                            .filter_by(ingredient_api_id=ingredient_api_id)
                            .first()
                        )
                    else:
                        print("Original")
                        ingredient = (
                            self.session.query(Ingredient).filter_by(ingredient=ingredient_info).first()
                        )

                    if not ingredient:
                        print("Ingr doestnt exist")
                        if not original_recipe:
                            ingredient = Ingredient(
                                ingredient_api_id=ingredient_info['id'],
                                ingredient=ingredient_info['originalString'] if 'originalString' in ingredient_info else
                                ingredient_info['original']
                            )
                        else:
                            print("making ingredients for original recipe")
                            ingredient = Ingredient(
                                ingredient_api_id=None,
                                ingredient=ingredient_info
                            )
                        print(f"NEW INGREDIENT: {ingredient}")
                        self.session.add(ingredient)
                        # self.session.commit()

                    recipe.ingredients.append(ingredient)
                    self.session.commit()
                except IntegrityError:
                    print("ingr rollback")
                    # Handle integrity error (e.g., duplicate API ID for ingredients)
                    self.session.rollback()

            return recipe  # Return the added recipe

        except IntegrityError:
            print("recipe rollback")
            # Handle integrity error (e.g., duplicate API ID for recipes)
            self.session.rollback()
            existing_recipe = self.session.query(Recipe).filter_by(recipe_api_id=recipe_api_id).first()
            if existing_recipe:
                print(f"Recipe with recipe_api_id {recipe_api_id} already exists.")
                return existing_recipe  # Return existing recipe instead of adding a new one

    def get_recipes(self, offset, page_size):
        # print("get all")
        recipes = self.session.query(Recipe).filter_by(original_recipe=False, ).offset(offset).limit(page_size).all()
        return recipes

    def get_all_favourite_recipes(self, offset, page_size):
        # print("get favs")
        recipes = self.session.query(Recipe).filter_by(favourite=True, ).offset(offset).limit(page_size).all()
        return recipes

    def get_all_original_recipes(self, offset, page_size):
        # print("get originals")
        recipes = self.session.query(Recipe).filter_by(original_recipe=True, ).offset(offset).limit(page_size).all()
        return recipes

    def search_for_recipes(self, criteria, search_text, original, favs):
        print("SEARCHING")
        print(criteria)
        print(search_text)

        # Build the dynamic OR clause for each criterion
        or_clauses = []
        and_clauses = []

        for criterion in criteria:
            if criterion == "title":
                print("title")
                or_clauses.append(Recipe.title.ilike(f'%{search_text}%'))
            elif criterion == "ingredient":
                print("ingr")
                # Ingredients is a list of ingredient names
                or_clauses.append(Ingredient.ingredient.ilike(f'%{search_text}%'))
            elif criterion == "cuisine":
                print("cuss")
                or_clauses.append(Recipe.cuisine.ilike(f'%{search_text}%'))
            elif criterion == "category":
                print("cattt")
                or_clauses.append(Recipe.food_category.ilike(f'%{search_text}%'))
            elif criterion == "vegan":
                print("vegaan")
                and_clauses.append(Recipe.vegan)
            elif criterion == "dairy-free":
                print("D FFFFF")
                and_clauses.append(Recipe.dairy_free)
            elif criterion == "gluten-free":
                print("GFFFFF")
                and_clauses.append(Recipe.gluten_free)
            elif criterion == "vegetarian":
                print("VEEEEG")
                and_clauses.append(Recipe.vegetarian)

        if original:
            and_clauses.append(Recipe.original_recipe)
        elif favs:
            and_clauses.append(Recipe.favourite)
        else:
            and_clauses.append(Recipe.original_recipe)

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

        # print(recipes)
        return recipes

    # Get the selected recipe from the recipe list
    def get_recipe(self, iid):
        recipe = self.session.query(Recipe).filter_by(recipe_api_id=iid, ).limit(1).first()
        return recipe

    # Get the original recipe selected from the recipe list
    def get_original_recipe(self, title):
        # print("GET ORIGINAL")
        recipe = self.session.query(Recipe).filter_by(original_recipe=True, title=title).limit(1).first()
        # print(recipe)
        return recipe

    def change_recipe_favourite_value(self, recipe):
        recipe.favourite = True if recipe.favourite is False else False
        self.session.commit()

    # Delete an original recipe
    def delete_recipe(self, title, instr):
        # Retrieve the recipe with the specified title
        recipe = self.session.query(Recipe).filter_by(original_recipe=True, title=title, instructions=instr, ).first()

        if recipe:
            # Delete the associated ingredients
            for ingredient in recipe.ingredients:
                self.session.delete(ingredient)

            # Delete the recipe itself
            self.session.delete(recipe)
            self.session.commit()
            print(f"Recipe with title '{title}' and associated ingredients deleted successfully.")
        else:
            print(f"No recipe found with title '{title}'.")

    # Edit recipe information
    # def edit_recipe(self, recipe, new_recipe_info):
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
            ingredient = self.session.query(Ingredient).filter_by(ingredient=ingredient_name).first()

            if not ingredient:
                ingredient = Ingredient(ingredient=ingredient_name)

            new_ingredients.append(ingredient)

        recipe.ingredients = new_ingredients

        self.session.commit()

    # def drop_tables(self):
    #     try:
    #         # Drop tables in reverse order to avoid foreign key constraints
    #         self.cursor.execute('DROP TABLE IF EXISTS recipes_ingredients;')
    #         self.cursor.execute('DROP TABLE IF EXISTS recipes;')
    #         self.cursor.execute('DROP TABLE IF EXISTS ingredients;')
    #
    #     finally:
    #         self.conn.commit()
    #         self.conn.close()
