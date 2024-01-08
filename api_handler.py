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

        print("EXTRACT API")
        print(response.json())
        return response.json()

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

        return recipes_data

    def load_random_recipes_from_api(self, recipe_count):
        querystring = {"number": str(recipe_count)}

        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/random"

        response = requests.get(url, headers=self.headers, params=querystring)

        return response.json()['recipes']

    def load_recipe_info_from_api(self, recipe_ids):
        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/informationBulk"

        querystring = {"ids": recipe_ids}

        response = requests.get(url, headers=self.headers, params=querystring)

        return response.json()

