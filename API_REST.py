from flask import Flask, jsonify
from flask_restful import Api, Resource
import pandas as pd
from flask_swagger_ui import get_swaggerui_blueprint
 
app = Flask(__name__)
api = Api(app)
 
# Charger les données CSV
data = pd.read_csv('index-egalite-fh-utf8.csv', delimiter=';')
 
# Configuration de Swagger
SWAGGER_URL = '/swagger'
API_URL = '/static/openapi.yaml'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "API de recherche par SIREN"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
 
class SirenSearch(Resource):
    def get(self, siren):
       
        # Rechercher le SIREN avec date la plus récente
        result = data[data['SIREN'].astype(str) == siren].sort_values(by='Année', ascending=False).head(1).to_dict(orient='records')
        if result:
            return jsonify(result)
        else:
            return {"message": "Aucun élément trouvé avec ce SIREN"}, 404
 
api.add_resource(SirenSearch, '/siren/<string:siren>')
 
if __name__ == '__main__':
    app.run(debug=True)