import sqlite3 as sq


class DBHandler:
    def __init__(self):
        self.conn = sq.connect('dish_dossier_db.db')  # Connect to the database
        self.cursor = self.conn.cursor()  # Create a cursor
        self.create_tables()

    def create_tables(self):
        # Create RECIPES table
        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipes (
                    recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipe_api_id INTEGER UNIQUE,
                    title TEXT NOT NULL,
                    prep_time INTEGER,
                    cook_time INTEGER,
                    total_cook_time INTEGER,
                    servings INTEGER,
                    image_url TEXT,
                    favourite BOOLEAN DEFAULT 0,
                    original_recipe BOOLEAN DEFAULT 0,
                    instructions TEXT,
                    ingredients TEXT);
            ''')

        # Create INGREDIENTS table
        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ingredients (
                    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ingredient_api_id INTEGER UNIQUE,
                    ingredient TEXT);
            ''')

        # Create recipes_ingredients table
        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipes_ingredients (
                    recipe_id INTEGER,
                    ingredient_id INTEGER,
                    FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
                    FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id));
            ''')

        # Commit the changes
        self.conn.commit()

    def insert_recipe(self, recipe_api_id, title, prep_time, cook_time, total_time,
                      servings, image, favourite, original_recipe, instructions):
        # Insert a recipe into RECIPES table
        self.cursor.execute('''
                INSERT INTO RECIPES (
                        recipe_api_id, title, prep_time, cook_time, total_time, servings, 
                        image, favourite, original_recipe, instructions
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''', (recipe_api_id, title, prep_time, cook_time, total_time, servings, image,
                  favourite, original_recipe, instructions,))

        self.conn.commit()

    def insert_ingredient(self, ingredient_api_id, ingredient):
        # Insert an ingredient into INGREDIENTS table
        self.cursor.execute('''
            INSERT INTO INGREDIENTS (ingredient_api_id, ingredient) VALUES (?, ?);
        ''', (ingredient_api_id, ingredient,))

        self.conn.commit()

    def link_recipe_and_ingredient(self, recipe_id, ingredient_id):
        # Link a recipe and an ingredient in the recipes_ingredients table
        self.cursor.execute('''
            INSERT INTO recipes_ingredients (recipe_id, ingredient_id) VALUES (?, ?);
        ''', (recipe_id, ingredient_id))

        self.conn.commit()

    def close_connection(self):
        self.conn.close()

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
