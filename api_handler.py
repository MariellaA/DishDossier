import requests


class RecipeAPIHandler():
    def __init__(self):
        self.api_key = self.load_api_key()
        self.headers = {"X-RapidAPI-Key": self.api_key,
                        "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"}

    @staticmethod
    def load_api_key():
        with open('api_key.txt', 'r') as file:
            key = file.read()
        return key

    def extract_recipe_from_website(self, url):
        print(url)
        api_url = "https://cookr-recipe-parser.p.rapidapi.com/getRecipe"

        querystring = {"source": url}

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "cookr-recipe-parser.p.rapidapi.com"
        }

        response = requests.get(api_url, headers=headers, params=querystring)

        print(response.json())
        extract_data = self.get_recipe_extractor_data(response.json())
        print(extract_data)
        return extract_data

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

    @staticmethod
    def get_recipe_extractor_data(response):
        recipe_data = []

        # for data in response:
        recipe_instructions = []
        # recipe_ingredients = []
        steps_count = 1

        for instruction in response["recipe"]["recipeInstructions"]:
            recipe_instructions.append(f"{steps_count}. {instruction['text']}\n")
            steps_count += 1

        # for ingredient in response["recipeIngredients"]:
        #     try:
        #         recipe_ingredients.append(f"{ingredient['quantity']}{ingredient['unit_measure']} {ingredient['label']}")
        #     except KeyError:
        #         recipe_ingredients.append(f"{ingredient['quantity']} {ingredient['label']}")

        image = response["recipe"]["image"][0]
        print(image)

        recipe_info = {
            "recipe_api_id": None,
            "title": response["recipe"]["name"],
            "prep_time": response["recipe"]["prepTimeOriginalFormat"][2:-1],
            "cook_time": response["recipe"]["cookTimeOriginalFormat"][2:-1],
            "total_cook_time": response["recipe"]["totalTimeOriginalFormat"][2:-1],
            "servings": response["recipe"]["recipeYield"],
            "image_url": image,
            "favourite": False,
            "original_recipe": True,
            "instructions": " ".join(recipe_instructions),
            "cuisine": response["recipe"]["recipeCuisine"][0] if response["recipe"]["recipeCuisine"] else "",  # recipe['cuisines'],
            "food_category": " ".join(response["recipe"]["recipeCategory"]),  # same thing as above
            "vegan": False,  # Diet information is not being provided by this API
            "vegetarian": False,
            "gluten_free": False,
            "dairy_free": False,
            "ingredients_data": response["recipe"]["recipeIngredients"],
        }

        recipe_data.append(recipe_info)

        return recipe_data

    @staticmethod
    def extract_information(response):
        recipes_data = []

        for recipe in response:
            recipe_instructions = []
            steps_count = 1

            for instructions in recipe["analyzedInstructions"]:
                if instructions["name"] != "":
                    recipe_instructions.append(f"{steps_count}. {instructions['name']}\n")
                    steps_count += 1

                for step in instructions["steps"]:
                    recipe_instructions.append(f"{steps_count}. {step['step']}\n")
                    steps_count += 1

            image = "assets/images/img.png"
            try:
                if recipe["image"] != '':
                    image = recipe["image"]
            except KeyError:
                pass

            recipe_info = {
                "recipe_api_id": recipe["id"],
                "title": recipe["title"],
                "prep_time": recipe["preparationMinutes"],
                "cook_time": recipe["cookingMinutes"],
                "total_cook_time": recipe["readyInMinutes"],
                "servings": recipe["servings"],
                "image_url": image,
                "favourite": False,
                "original_recipe": False,
                "instructions": " ".join(recipe_instructions),
                "cuisine": " ".join(recipe["cuisines"]),  # recipe['cuisines'],
                "food_category": " ".join(recipe["dishTypes"]),  # same thing as above
                "vegan": recipe["vegan"],
                "vegetarian": recipe["vegetarian"],
                "gluten_free": recipe["glutenFree"],
                "dairy_free": recipe["dairyFree"],
                "ingredients_data": recipe["extendedIngredients"],
            }

            recipes_data.append(recipe_info)

        return recipes_data
