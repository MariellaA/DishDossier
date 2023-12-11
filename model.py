import certifi
from kivy.event import EventDispatcher
from kivy.properties import ListProperty
import requests


class DishDossierModel(EventDispatcher):
    recipes = ListProperty([])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recipes = [{'id': 656791, 'title': 'Pork Menudo', 'prep_time': -1, 'cooking_time': -1, 'ready_in_time': 45,
                         'servings': 4, 'image': 'img_1.png',
                         'instructions': "<ol><li>Heat your wok or big kawali. Make sure it's hot before you put oil. Fry the potatoes until half-cooked. Set aside.</li><li>On the same pan, add butter and garlic. Do not burn the garlic.</li><li>Add the pork, tomatoes, onions and bell pepper. Add salt and pepper to taste. You can also add 1 pork cube for a richer flavor. Reduce to low heat. Juices will eventually come out from the vegetables so no need to add water. Cover, stirring occasionally. Simmer until pork is tender or until the liquid has almost dried up leaving a thick sauce.</li><li>Add the liver, cover for about 5 minutes. I'm adding the liver at a later part because we don't want to overcook it. Liver cooks fast and it can be tough if overdone.</li><li>Add the potatoes, carrots, green peas and raisins (and the rest of the ingredients, if any). Simmer for 15 more minutes stirring occasionally.</li><li>Serve with steamed rice.</li></ol>"},
                        {'id': 656791, 'title': 'Pork Menudo', 'prep_time': -1, 'cooking_time': -1, 'ready_in_time': 45,
                         'servings': 4, 'image': 'img_1.png',
                         'instructions': "<ol><li>Heat your wok or big kawali. Make sure it's hot before you put oil. Fry the potatoes until half-cooked. Set aside.</li><li>On the same pan, add butter and garlic. Do not burn the garlic.</li><li>Add the pork, tomatoes, onions and bell pepper. Add salt and pepper to taste. You can also add 1 pork cube for a richer flavor. Reduce to low heat. Juices will eventually come out from the vegetables so no need to add water. Cover, stirring occasionally. Simmer until pork is tender or until the liquid has almost dried up leaving a thick sauce.</li><li>Add the liver, cover for about 5 minutes. I'm adding the liver at a later part because we don't want to overcook it. Liver cooks fast and it can be tough if overdone.</li><li>Add the potatoes, carrots, green peas and raisins (and the rest of the ingredients, if any). Simmer for 15 more minutes stirring occasionally.</li><li>Serve with steamed rice.</li></ol>"},
                        {'id': 656791, 'title': 'Pork Menudo', 'prep_time': -1, 'cooking_time': -1, 'ready_in_time': 45,
                         'servings': 4, 'image': 'img_1.png',
                         'instructions': "<ol><li>Heat your wok or big kawali. Make sure it's hot before you put oil. Fry the potatoes until half-cooked. Set aside.</li><li>On the same pan, add butter and garlic. Do not burn the garlic.</li><li>Add the pork, tomatoes, onions and bell pepper. Add salt and pepper to taste. You can also add 1 pork cube for a richer flavor. Reduce to low heat. Juices will eventually come out from the vegetables so no need to add water. Cover, stirring occasionally. Simmer until pork is tender or until the liquid has almost dried up leaving a thick sauce.</li><li>Add the liver, cover for about 5 minutes. I'm adding the liver at a later part because we don't want to overcook it. Liver cooks fast and it can be tough if overdone.</li><li>Add the potatoes, carrots, green peas and raisins (and the rest of the ingredients, if any). Simmer for 15 more minutes stirring occasionally.</li><li>Serve with steamed rice.</li></ol>"},
                        {'id': 656791, 'title': 'Pork Menudo', 'prep_time': -1, 'cooking_time': -1, 'ready_in_time': 45,
                         'servings': 4, 'image': 'img_1.png',
                         'instructions': "<ol><li>Heat your wok or big kawali. Make sure it's hot before you put oil. Fry the potatoes until half-cooked. Set aside.</li><li>On the same pan, add butter and garlic. Do not burn the garlic.</li><li>Add the pork, tomatoes, onions and bell pepper. Add salt and pepper to taste. You can also add 1 pork cube for a richer flavor. Reduce to low heat. Juices will eventually come out from the vegetables so no need to add water. Cover, stirring occasionally. Simmer until pork is tender or until the liquid has almost dried up leaving a thick sauce.</li><li>Add the liver, cover for about 5 minutes. I'm adding the liver at a later part because we don't want to overcook it. Liver cooks fast and it can be tough if overdone.</li><li>Add the potatoes, carrots, green peas and raisins (and the rest of the ingredients, if any). Simmer for 15 more minutes stirring occasionally.</li><li>Serve with steamed rice.</li></ol>"},
                        {'id': 656791, 'title': 'Pork Menudo', 'prep_time': -1, 'cooking_time': -1, 'ready_in_time': 45,
                         'servings': 4, 'image': 'img_1.png',
                         'instructions': "<ol><li>Heat your wok or big kawali. Make sure it's hot before you put oil. Fry the potatoes until half-cooked. Set aside.</li><li>On the same pan, add butter and garlic. Do not burn the garlic.</li><li>Add the pork, tomatoes, onions and bell pepper. Add salt and pepper to taste. You can also add 1 pork cube for a richer flavor. Reduce to low heat. Juices will eventually come out from the vegetables so no need to add water. Cover, stirring occasionally. Simmer until pork is tender or until the liquid has almost dried up leaving a thick sauce.</li><li>Add the liver, cover for about 5 minutes. I'm adding the liver at a later part because we don't want to overcook it. Liver cooks fast and it can be tough if overdone.</li><li>Add the potatoes, carrots, green peas and raisins (and the rest of the ingredients, if any). Simmer for 15 more minutes stirring occasionally.</li><li>Serve with steamed rice.</li></ol>"},
                        {'id': 656791, 'title': 'Pork Menudo', 'prep_time': -1, 'cooking_time': -1, 'ready_in_time': 45,
                         'servings': 4, 'image': 'img_1.png',
                         'instructions': "<ol><li>Heat your wok or big kawali. Make sure it's hot before you put oil. Fry the potatoes until half-cooked. Set aside.</li><li>On the same pan, add butter and garlic. Do not burn the garlic.</li><li>Add the pork, tomatoes, onions and bell pepper. Add salt and pepper to taste. You can also add 1 pork cube for a richer flavor. Reduce to low heat. Juices will eventually come out from the vegetables so no need to add water. Cover, stirring occasionally. Simmer until pork is tender or until the liquid has almost dried up leaving a thick sauce.</li><li>Add the liver, cover for about 5 minutes. I'm adding the liver at a later part because we don't want to overcook it. Liver cooks fast and it can be tough if overdone.</li><li>Add the potatoes, carrots, green peas and raisins (and the rest of the ingredients, if any). Simmer for 15 more minutes stirring occasionally.</li><li>Serve with steamed rice.</li></ol>"},
                        {'id': 656791, 'title': 'Pork Menudo', 'prep_time': -1, 'cooking_time': -1, 'ready_in_time': 45,
                         'servings': 4, 'image': 'img_1.png',
                         'instructions': "<ol><li>Heat your wok or big kawali. Make sure it's hot before you put oil. Fry the potatoes until half-cooked. Set aside.</li><li>On the same pan, add butter and garlic. Do not burn the garlic.</li><li>Add the pork, tomatoes, onions and bell pepper. Add salt and pepper to taste. You can also add 1 pork cube for a richer flavor. Reduce to low heat. Juices will eventually come out from the vegetables so no need to add water. Cover, stirring occasionally. Simmer until pork is tender or until the liquid has almost dried up leaving a thick sauce.</li><li>Add the liver, cover for about 5 minutes. I'm adding the liver at a later part because we don't want to overcook it. Liver cooks fast and it can be tough if overdone.</li><li>Add the potatoes, carrots, green peas and raisins (and the rest of the ingredients, if any). Simmer for 15 more minutes stirring occasionally.</li><li>Serve with steamed rice.</li></ol>"},
                        {'id': 656791, 'title': 'Pork Menudo', 'prep_time': -1, 'cooking_time': -1, 'ready_in_time': 45,
                         'servings': 4, 'image': 'img_1.png',
                         'instructions': "<ol><li>Heat your wok or big kawali. Make sure it's hot before you put oil. Fry the potatoes until half-cooked. Set aside.</li><li>On the same pan, add butter and garlic. Do not burn the garlic.</li><li>Add the pork, tomatoes, onions and bell pepper. Add salt and pepper to taste. You can also add 1 pork cube for a richer flavor. Reduce to low heat. Juices will eventually come out from the vegetables so no need to add water. Cover, stirring occasionally. Simmer until pork is tender or until the liquid has almost dried up leaving a thick sauce.</li><li>Add the liver, cover for about 5 minutes. I'm adding the liver at a later part because we don't want to overcook it. Liver cooks fast and it can be tough if overdone.</li><li>Add the potatoes, carrots, green peas and raisins (and the rest of the ingredients, if any). Simmer for 15 more minutes stirring occasionally.</li><li>Serve with steamed rice.</li></ol>"},
                        {'id': 656791, 'title': 'Pork Menudo', 'prep_time': -1, 'cooking_time': -1, 'ready_in_time': 45,
                         'servings': 4, 'image': 'img_1.png',
                         'instructions': "<ol><li>Heat your wok or big kawali. Make sure it's hot before you put oil. Fry the potatoes until half-cooked. Set aside.</li><li>On the same pan, add butter and garlic. Do not burn the garlic.</li><li>Add the pork, tomatoes, onions and bell pepper. Add salt and pepper to taste. You can also add 1 pork cube for a richer flavor. Reduce to low heat. Juices will eventually come out from the vegetables so no need to add water. Cover, stirring occasionally. Simmer until pork is tender or until the liquid has almost dried up leaving a thick sauce.</li><li>Add the liver, cover for about 5 minutes. I'm adding the liver at a later part because we don't want to overcook it. Liver cooks fast and it can be tough if overdone.</li><li>Add the potatoes, carrots, green peas and raisins (and the rest of the ingredients, if any). Simmer for 15 more minutes stirring occasionally.</li><li>Serve with steamed rice.</li></ol>"},
                        {'id': 656791, 'title': 'Pork Menudo', 'prep_time': -1, 'cooking_time': -1, 'ready_in_time': 45,
                         'servings': 4, 'image': 'img_1.png',
                         'instructions': "<ol><li>Heat your wok or big kawali. Make sure it's hot before you put oil. Fry the potatoes until half-cooked. Set aside.</li><li>On the same pan, add butter and garlic. Do not burn the garlic.</li><li>Add the pork, tomatoes, onions and bell pepper. Add salt and pepper to taste. You can also add 1 pork cube for a richer flavor. Reduce to low heat. Juices will eventually come out from the vegetables so no need to add water. Cover, stirring occasionally. Simmer until pork is tender or until the liquid has almost dried up leaving a thick sauce.</li><li>Add the liver, cover for about 5 minutes. I'm adding the liver at a later part because we don't want to overcook it. Liver cooks fast and it can be tough if overdone.</li><li>Add the potatoes, carrots, green peas and raisins (and the rest of the ingredients, if any). Simmer for 15 more minutes stirring occasionally.</li><li>Serve with steamed rice.</li></ol>"},
                        {'id': 656791, 'title': 'Pork Menudo', 'prep_time': -1, 'cooking_time': -1, 'ready_in_time': 45,
                         'servings': 4, 'image': 'img_1.png',
                         'instructions': "<ol><li>Heat your wok or big kawali. Make sure it's hot before you put oil. Fry the potatoes until half-cooked. Set aside.</li><li>On the same pan, add butter and garlic. Do not burn the garlic.</li><li>Add the pork, tomatoes, onions and bell pepper. Add salt and pepper to taste. You can also add 1 pork cube for a richer flavor. Reduce to low heat. Juices will eventually come out from the vegetables so no need to add water. Cover, stirring occasionally. Simmer until pork is tender or until the liquid has almost dried up leaving a thick sauce.</li><li>Add the liver, cover for about 5 minutes. I'm adding the liver at a later part because we don't want to overcook it. Liver cooks fast and it can be tough if overdone.</li><li>Add the potatoes, carrots, green peas and raisins (and the rest of the ingredients, if any). Simmer for 15 more minutes stirring occasionally.</li><li>Serve with steamed rice.</li></ol>"}]

        # id:, title:, prep_in_mins:, cooking_mins:, ready_in_mins:, img:, instr:,
        # self.recipes = []
        self.categories = []
        # self.key = "98aae24ecb20497c8a85c16500247251f"
        self.headers = {"X-RapidAPI-Key": "0edc1b1db1msh62b5a54207e582fp1a8302jsnb97729ff79f0",
                        "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"}

        # self.load_recipes_from_api()
        # self.load_initial_recipes()

    # def load_initial_recipes(self):
    #     self.recipes.extend(["M", "b", "c", "d", "e", "f", "g", "h"])

    def load_recipes_from_api(self):
        querystring = {"number": "1"}

        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/random"

        response = requests.get(url, headers=self.headers, params=querystring)

        print(response.json())
        for recipe in response.json()['recipes']:
            self.recipes.append({"id": recipe["id"],
                                 "title": recipe["title"],
                                 "prep_time": recipe["preparationMinutes"],
                                 "cooking_time": recipe["cookingMinutes"],
                                 "ready_in_time": recipe["readyInMinutes"],
                                 "servings": recipe["servings"],
                                 "image": "img_1.png",  # recipe["image"] if recipe["image"] else
                                 "instructions": recipe["instructions"]})

        print(self.recipes)
