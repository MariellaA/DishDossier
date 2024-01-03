import requests


class RecipeAPIHandler():
    def __init__(self):
        self.headers = {"X-RapidAPI-Key": self.load_api_key(),
                        "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"}

    @staticmethod
    def load_api_key():
        with open('api_key.txt', 'r') as file:
            key = file.read()
        return key

    def load_random_recipes_from_api(self):
        ### decide on how many random recipes are needed
        querystring = {"number": "1"}

        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/random"

        response = requests.get(url, headers=self.headers, params=querystring)

        recipes_data = []
        for recipe in response.json()['recipes']:
            print(recipe)
            cuisines = " ".join(recipe['dishTypes'])
            # print(cuisines)

            recipe_instructions = []
            steps_count = 1

            for instructions in recipe['analyzedInstructions']:
                if instructions['name'] != "":
                    recipe_instructions.append(f"{steps_count}. {instructions['name']}\n")
                    steps_count += 1

                for step in instructions["steps"]:
                    recipe_instructions.append(f"{steps_count}. {step['step']}\n")
                    steps_count += 1

            image = 'assets/images/img.png'
            try:
                if recipe['image'] != '':
                    image = recipe['image']
            except KeyError:
                pass

            print(f"RECIPE INSTR {recipe_instructions}")

            recipe_info = {
                "recipe_api_id": recipe['id'],
                "title": recipe['title'],
                "prep_time": recipe['preparationMinutes'],
                "cook_time": recipe['cookingMinutes'],
                "total_cook_time": recipe['readyInMinutes'],
                "servings": recipe['servings'],
                "image_url": image,
                "favourite": False,
                "original_recipe": False,
                # "instructions": recipe['instructions'],
                "instructions": " ".join(recipe_instructions),
                "cuisine": " ".join(recipe['cuisines']),  # recipe['cuisines'],
                "food_category": " ".join(recipe['dishTypes']),  # same thing as above
                "vegan": recipe['vegan'],
                "vegetarian": recipe['vegetarian'],
                "gluten_free": recipe['glutenFree'],
                "dairy_free": recipe['dairyFree'],
                "ingredients_data": recipe['extendedIngredients'],
            }

            recipes_data.append(recipe_info)

        return recipes_data
