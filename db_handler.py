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
    ingredients = relationship('Ingredient', secondary=recipes_ingredients)  # , cascade='all, delete-orphan)


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
                   servings, image_url, favourite, original_recipe, instructions, ingredients_data):
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
                instructions=instructions
            )

            # Add the Recipe to the database
            self.session.add(recipe)
            # self.session.commit()
            print("ADDING TO DB")
            print(ingredients_data)

            # Check for existing ingredients and add only new ones
            for ingredient_info in ingredients_data:
                # TODO: When using the API check if relationship between new recipes with already
                #  existing ingredients is added to recipes_ingredient; affects ingredient displaying
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
                or_clauses.append(Recipe.title.ilike(f'%{search_text}%'))
            elif criterion == "ingredient":
                # Assuming ingredients is a list of ingredient names
                or_clauses.append(Ingredient.ingredient.ilike(f'%{search_text}%'))

        if original:
            and_clauses.append(Recipe.original_recipe == True)
        elif favs:
            and_clauses.append(Recipe.favourite == True)
        else:
            and_clauses.append(Recipe.original_recipe == False)


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
    def edit_recipe(self, recipe, new_recipe_info):
        recipe.title = new_recipe_info[1]
        recipe.prep_time = new_recipe_info[2]
        recipe.cook_time = new_recipe_info[3]
        recipe.total_cook_time = new_recipe_info[4]
        recipe.servings = new_recipe_info[5]
        recipe.image_url = new_recipe_info[6]
        recipe.instructions = new_recipe_info[9]

        new_ingredients = []
        for ingredient_name in new_recipe_info[10]:
            ingredient = self.session.query(Ingredient).filter_by(ingredient=ingredient_name).first()

            if not ingredient:
                ingredient = Ingredient(ingredient=ingredient_name)

            new_ingredients.append(ingredient)

        recipe.ingredients = new_ingredients

        self.session.commit()

    def drop_tables(self):
        try:
            # Drop tables in reverse order to avoid foreign key constraints
            self.cursor.execute('DROP TABLE IF EXISTS recipes_ingredients;')
            self.cursor.execute('DROP TABLE IF EXISTS recipes;')
            self.cursor.execute('DROP TABLE IF EXISTS ingredients;')

        finally:
            self.conn.commit()
            self.conn.close()


# # Commit the changes
# conn.commit()
#
# # Close the connection
# conn.close()


# def add_to_database():
#     # Connect to the database
#     conn = sq.connect("dish_dossier_db.db")
#
#     # Create a cursor
#     cur = conn.cursor()
#     cur.execute("""INSERT INTO recipes VALUES (:title, :prep_time, :cook_time, :total_cook_time, :servings, :image_url,
#                     :fav, :original, :instructions, :description, :ingredients, :nutrition)
#                     {
#                         'title':
#                     }
#                     """)
#
#     # Add a record
#
#     # Commit the changes
#     conn.commit()
#
#     # Close the connection
#     conn.close()


def show_data():
    pass
