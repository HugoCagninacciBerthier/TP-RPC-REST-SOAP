from flask import Flask
from flask_jsonrpc import JSONRPC
import pandas as pd
 
app = Flask(__name__)
 
#Activation de l'interface web pour les appels JSON-RPC
jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)
 
# Charger les données avec SIREN
data = pd.read_csv('index-egalite-fh-utf8.csv', delimiter=';', encoding='utf-8', dtype={'SIREN': str})
 
@jsonrpc.method('api.search_by_siren')
def search_by_siren(siren: str) -> dict:
    """
    Recherche une entreprise par son SIREN via JSON-RPC et retourne l'entrée la plus récente.
    """
    siren = str(siren).strip()
    filtered_data = data[data['SIREN'].str.strip() == siren]
 
    if not filtered_data.empty:
        # Sélectionne par l'année la plus récente
        most_recent = filtered_data.loc[filtered_data['Année'].idxmax()]

        return most_recent.to_dict()
   
    return {'error': 'SIREN not found'}
 
if __name__ == '__main__':
    app.run(debug=True)
 
 