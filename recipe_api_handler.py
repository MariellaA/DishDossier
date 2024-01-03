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

    def find_recipe_from_api(self, search_by, look_for, number):
        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/complexSearch"

        querystring = {"number": str(number)}
        intolerances = []
        diet = []

        for category in search_by:
            if category == "title":
                querystring["query"] = look_for
            elif category == "ingredient":
                querystring["includeIngredients"] = look_for
            elif category == "cuisine":
                querystring["cuisine"] = look_for
            elif category == "category":
                querystring["type"] = look_for
            elif category == "vegan":
                diet.append("vegan")
            elif category == "dairy-free":
                intolerances.append("dairy")
            elif category == "gluten-free":
                intolerances.append("gluten")
            elif category == "vegetarian":
                diet.append("vegetarian")

        if intolerances:
            querystring["intolerances"] = ", ".join(intolerances)
        if diet:
            querystring["diet"] = ", ".join(diet)

        response = requests.get(url, headers=self.headers, params=querystring)
        recipes = response.json()["results"]

        recipe_ids = ""
        for recipe in recipes:
            recipe_ids += str(recipe["id"]) + ", "

        recipes_data = self.load_recipe_info_from_api(recipe_ids.strip(", "))
        new_recipes = self.extract_information(recipes_data)

        return new_recipes

    def load_random_recipes_from_api(self, recipe_count):
        querystring = {"number": str(recipe_count)}

        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/random"

        response = requests.get(url, headers=self.headers, params=querystring)

        recipes_data = self.extract_information(response.json()['recipes'])

        return recipes_data

    def load_recipe_info_from_api(self, recipe_ids):
        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/informationBulk"

        querystring = {"ids": recipe_ids}

        response = requests.get(url, headers=self.headers, params=querystring)

        return response.json()

    def extract_information(self, response):
        recipes_data = []

        for recipe in response:
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
