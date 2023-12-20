from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, Boolean, Text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
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
    ingredients = relationship('Ingredient', secondary=recipes_ingredients)


class Ingredient(Base):
    __tablename__ = 'ingredients'
    ingredient_id = Column(Integer, primary_key=True, autoincrement=True)
    ingredient_api_id = Column(Integer, unique=True, nullable=True)
    ingredient = Column(String)


class DBHandler:
    def __init__(self, database_url='sqlite:///dish_dossier_db.db'):
        # self.conn = sq.connect('dish_dossier_db.db')  # Connect to the database
        # self.cursor = self.conn.cursor()  # Create a cursor
        # self.create_tables()

        self.engine = create_engine(database_url, echo=True)
        self.create_tables()
        self.session = sessionmaker(bind=self.engine)()
        # self.create_session()

    def check_if_recipe_exists(self, recipe_api_id):
        # Check if the recipe exists in the database
        self.cursor.execute("SELECT * FROM recipes WHERE recipe_api_id = ?", (recipe_api_id,))
        existing_recipe = self.cursor.fetchone()

        print(existing_recipe)

        if existing_recipe:
            print(f"Recipe '{existing_recipe[1]}' found in the database.")
            self.conn.close()
            return existing_recipe
        else:
            print(f"Recipe with API ID {recipe_api_id} not found in the database. Fetching from API.")
            # self.conn.close()

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    # def create_session(self):
    #     Session = sessionmaker(bind=self.engine)

    # def create_tables(self):
    #     # Create RECIPES table
    #     self.cursor.execute('''
    #             CREATE TABLE IF NOT EXISTS recipes (
    #                 recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                 recipe_api_id INTEGER UNIQUE,
    #                 title TEXT NOT NULL,
    #                 prep_time INTEGER,
    #                 cook_time INTEGER,
    #                 total_cook_time INTEGER,
    #                 servings INTEGER,
    #                 image_url TEXT,
    #                 favourite BOOLEAN DEFAULT 0,
    #                 original_recipe BOOLEAN DEFAULT 0,
    #                 instructions TEXT);
    #         ''')
    #
    #     # Create INGREDIENTS table
    #     self.cursor.execute('''
    #             CREATE TABLE IF NOT EXISTS ingredients (
    #                 ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                 ingredient_api_id INTEGER UNIQUE,
    #                 ingredient TEXT);
    #         ''')
    #
    #     # Create recipes_ingredients table
    #     self.cursor.execute('''
    #             CREATE TABLE IF NOT EXISTS recipes_ingredients (
    #                 recipe_id INTEGER,
    #                 ingredient_id INTEGER,
    #                 FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
    #                 FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id));
    #         ''')
    #
    #     # Commit the changes
    #     self.conn.commit()

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
            self.session.commit()

            # Check for existing ingredients and add only new ones
            for ingredient_info in ingredients_data:
                print(ingredient_info)
                try:
                    ingredient = Ingredient(
                        ingredient_api_id=ingredient_info['id'],
                        ingredient=ingredient_info['originalString'] if 'originalString' in ingredient_info else
                        ingredient_info['original']
                    )
                    self.session.add(ingredient)
                    self.session.commit()
                    recipe.ingredients.append(ingredient)
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

        # try:
        #     # Insert a recipe into RECIPES table
        #     self.cursor.execute('''
        #             INSERT INTO RECIPES (
        #                     recipe_api_id, title, prep_time, cook_time, total_cook_time, servings,
        #                     image_url, favourite, original_recipe, instructions
        #             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        #         ''', (recipe_api_id, title, prep_time, cook_time, total_time, servings, image,
        #               favourite, original_recipe, instructions,))
        #
        #     recipe_id = self.cursor.lastrowid
        #
        #     print(recipe_id)
        #
        #     self.conn.commit()
        #     # self.close_connection()
        #
        #     return recipe_id
        # except sq.IntegrityError as e:
        #     print(f"Recipes ALREADY EXISTS: {recipe_api_id}")
        #     pass

    def insert_ingredient(self, ingredient_api_id, ingredient):
        # Insert an ingredient into INGREDIENTS table
        try:
            self.cursor.execute('''
                INSERT INTO INGREDIENTS (ingredient_api_id, ingredient) VALUES (?, ?);
            ''', (ingredient_api_id, ingredient,))

            ingredient_id = self.cursor.lastrowid

            self.conn.commit()
            # self.close_connection()

            return ingredient_id
        except sq.IntegrityError as e:
            print(ingredient)
            print("Duplicate ingredient")
            pass

    def link_recipe_and_ingredient(self, recipe_id, ingredient_id):
        # Link a recipe and an ingredient in the recipes_ingredients table
        self.cursor.execute('''
            INSERT INTO recipes_ingredients (recipe_id, ingredient_id) VALUES (?, ?);
        ''', (recipe_id, ingredient_id))

        self.conn.commit()
        # self.close_connection()

    # def close_connection(self):
    #     self.conn.close()

    def get_all_recipes(self):
        recipes = self.session.query(Recipe).all()
        return recipes

    def get_all_favourite_recipes(self):
        recipes = self.session.query(Recipe).filter_by(favourite=True,).all()
        return recipes

    def get_original_recipes(self):
        recipes = self.session.query(Recipe).filter_by(original_recipe=True,).all()
        return recipes

    def get_recipe(self, iid):
        recipe = self.session.query(Recipe).filter_by(recipe_api_id=iid,).limit(1).first()
        return recipe

    def change_recipe_favourite_value(self, recipe):
        recipe.favourite = True if recipe.favourite == False else False
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
