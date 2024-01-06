from api_handler import RecipeAPIHandler
from db_handler import DBHandler
from dish_dossier_app import DishDossierApp


if __name__ == "__main__":
    api_handler = RecipeAPIHandler()
    db = DBHandler()
    DishDossierApp(api_handler, db).run()