class Recipe:
    # def __init__(self, id, title, prep_time, cooking_time, ready_in_time, servings, image, instructions):
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.title = kwargs.get('title', None)
        self.prep_time = kwargs.get('prep_time', None)
        self.cooking_time = kwargs.get('cooking_time', None)
        self.ready_in_time = kwargs.get('ready_in_time', None)
        self.servings = kwargs.get('servings', None)
        self.image = kwargs.get('image', None)
        self.instructions = kwargs.get('instructions', None)

