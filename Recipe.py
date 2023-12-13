class Recipe:
    # def __init__(self, id, title, prep_time, cooking_time, ready_in_time, servings, image, instructions):
    def __init__(self, info):
        self.id = str(info.get('id', None))
        self.title = str(info.get('title', None))
        self.prep_time = str(info.get('prep_time', None))
        self.cooking_time = str(info.get('cooking_time', None))
        self.total_time = str(info.get('ready_in_time', None))
        self.servings = str(info.get('servings', None))
        self.image = info.get('image', None)
        self.instructions = info.get('instructions', None)
        self.favourite = False
        self.extendedIngredients = info.get('extendedIngredients', None)

