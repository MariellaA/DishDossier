import requests


class RecipeAPIHandler():
    def __init__(self):
        self.headers = {"X-RapidAPI-Key": self.load_api_key(),
                        "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"}
        # print(self.load_api_key())

    @staticmethod
    def load_api_key():
        with open('api_key.txt', 'r') as file:
            key = file.read()
        return key

    def load_random_recipes_from_api(self):
        querystring = {"number": "1"}

        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/random"

        response = requests.get(url, headers=self.headers, params=querystring)

        return response.json()['recipes']

