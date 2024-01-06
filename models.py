from sqlalchemy import Table, Column, Integer, ForeignKey, String, Boolean, Text
from sqlalchemy.orm import declarative_base, relationship

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
