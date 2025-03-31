#pip install Flask Flask-RESTful pandas Flask-Swagger-UI Flask-JSONRPC zeep lxml
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import pandas as pd
from flask_swagger_ui import get_swaggerui_blueprint
from flask_jsonrpc import JSONRPC
from csv import DictReader
from zeep import Plugin, CachingClient
from zeep.wsdl.utils import etree_to_string
from zeep.helpers import serialize_object
from lxml import etree
 
app = Flask(__name__)
api = Api(app)


#############--DEFINITION DES CONSTANTES--###################

# Initialisation de JSON-RPC avec Flask, en activant l'interface web pour les appels JSON-RPC
jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)

# Charger les données avec SIREN en tant que chaîne et Année comme entier
data = pd.read_csv('index-egalite-fh-utf8.csv', delimiter=';', encoding='utf-8', dtype={'SIREN': str})
 
 
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

#Pour que ca fonctionne on doit installer differentes bibliotheques avec la commande 
# pip install Flask lxml zeep


# Chargement de la base de donnes CSV
egapro_data = {}
with open("index-egalite-fh-utf8.csv", encoding="utf-8") as csv:
    reader = DictReader(csv, delimiter=";", quotechar='"')
    for row in reader:
        if egapro_data.get(row["SIREN"]) is None:
            egapro_data[row["SIREN"]] = row
        elif egapro_data[row["SIREN"]]["Année"] < row["Année"]:
            egapro_data[row["SIREN"]].update(row)


# Définition du WSDL (description du service SOAP)
wsdl_template = """
<?xml version="1.0" encoding="UTF-8"?>
<!-- Déclaration XML standard, indiquant la version et l'encodage utilisés -->
<definitions name="EgaProService"
             targetNamespace="http://localhost:5000/egapro.wsdl"
             xmlns:tns="http://localhost:5000/egapro.wsdl"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
             xmlns:soap12="http://schemas.xmlsoap.org/wsdl/soap12/"
             xmlns:wsa="http://www.w3.org/2005/08/addressing"
             xmlns:wsrm="http://docs.oasis-open.org/ws-rx/wsrm/200702"
             xmlns:wsp="http://schemas.xmlsoap.org/ws/2002/12/policy"
             xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">

    <!-- Définition des types de données utilisés dans le WSDL -->
    <types>
        <!-- Schéma XML définissant les types de données complexes utilisés dans ce service -->
        <xsd:schema targetNamespace="http://localhost:5000/egapro.wsdl">
            <!-- Type complexe représentant la réponse du service GetSiren -->
            <xsd:complexType name="EgaProResponse">
                <!-- Séquence d'éléments qui composent la réponse -->
                <xsd:sequence>
                    <!-- Chaque élément représente une donnée spécifique renvoyée par le service -->
                    <xsd:element name="Année" type="xsd:string"/>
                    <xsd:element name="Structure" type="xsd:string"/>
                    <xsd:element name="Tranche_deffectifs" type="xsd:string"/>
                    <xsd:element name="SIREN" type="xsd:string"/>
                    <xsd:element name="Raison_Sociale" type="xsd:string"/>
                    <!-- Éléments optionnels, peuvent ne pas être présents dans la réponse -->
                    <xsd:element name="Nom_UES" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="Entreprises_UES_SIREN" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="Région" type="xsd:string"/>
                    <xsd:element name="Département" type="xsd:string"/>
                    <xsd:element name="Pays" type="xsd:string"/>
                    <xsd:element name="Code_NAF" type="xsd:string"/>
                    <xsd:element name="Note_Ecart_rémunération" type="xsd:int"/>
                    <xsd:element name="Note_Ecart_taux_daugmentation_hors_promotion" type="xsd:int"/>
                    <xsd:element name="Note_Ecart_taux_de_promotion" type="xsd:int"/>
                    <xsd:element name="Note_Ecart_taux_daugmentation" type="xsd:int" minOccurs="0"/>
                    <xsd:element name="Note_Retour_congé_maternité" type="xsd:int"/>
                    <xsd:element name="Note_Hautes_rémunérations" type="xsd:int"/>
                    <xsd:element name="Note_Index" type="xsd:int"/>
                </xsd:sequence>
            </xsd:complexType>
        </xsd:schema>
    </types>

    <!-- Définition des messages échangés entre le client et le service -->
    <message name="GetSirenRequest">
        <!-- Message de requête contenant le numéro SIREN -->
        <part name="siren" type="xsd:string"/>
    </message>

    <message name="GetSirenResponse">
        <!-- Message de réponse contenant les données de l'entreprise -->
        <part name="data" type="tns:EgaProResponse"/>
    </message>

    <!-- Définition des opérations disponibles dans le service -->
    <portType name="EgaProPortType">
        <!-- Opération GetSiren qui prend une requête et renvoie une réponse -->
        <operation name="GetSiren">
            <input message="tns:GetSirenRequest"/>
            <output message="tns:GetSirenResponse"/>
        </operation>
    </portType>

    <!-- Définition de la liaison entre les opérations et le protocole SOAP -->
    <binding name="EgaProBinding" type="tns:EgaProPortType">
        <!-- Utilisation du style RPC pour les appels SOAP -->
        <soap:binding style="rpc" transport="http://schemas.xmlsoap.org/soap/http"/>

        <!-- Politique de sécurité (optionnelle) -->
        <wsp:Policy>
            <wsp:ExactlyOne>
                <wsp:All>
                    <!-- Sécurité basée sur un jeton utilisateur et un horodatage -->
                    <wsse:Security>
                        <wsse:UsernameToken/>
                        <wsse:Timestamp/>
                    </wsse:Security>
                    <!-- Assertion de gestion des messages fiables -->
                    <wsrm:RMAssertion/>
                </wsp:All>
            </wsp:ExactlyOne>
        </wsp:Policy>

        <!-- Définition de l'opération GetSiren dans le contexte SOAP -->
        <operation name="GetSiren">
            <soap:operation soapAction="http://localhost:5000/GetSiren"/>
            <input>
                <soap:body use="literal"/>
            </input>
            <output>
                <soap:body use="literal"/>
            </output>
        </operation>
    </binding>

    <!-- Définition du service et de son point de terminaison -->
    <service name="EgaProService">
        <!-- Port de service utilisant la liaison définie -->
        <port name="EgaProPort" binding="tns:EgaProBinding">
            <!-- Adresse SOAP où le service est accessible -->
            <soap:address location="http://localhost:5000/soap"/>
            <!-- Référence de point de terminaison (optionnelle) -->
            <wsa:EndpointReference>
                <wsa:Address>http://localhost:5000/soap</wsa:Address>
            </wsa:EndpointReference>
        </port>
    </service>
</definitions>
"""

####################--REST--#################################

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

########################--JSON RPC--#################################
@jsonrpc.method('api.search_by_siren')
def search_by_siren(siren: str) -> dict:
    """
    Recherche une entreprise par son SIREN via JSON-RPC et retourne l'entrée la plus récente.
    """
    siren = str(siren).strip()
    filtered_data = data[data['SIREN'].str.strip() == siren]

    if not filtered_data.empty:
        # Sélectionner l'entrée avec l'année la plus récente
        most_recent = filtered_data.loc[filtered_data['Année'].idxmax()]
        # Conversion de l'entrée en dictionnaire et retour de celle-ci
        return most_recent.to_dict()
    
    return {'error': 'SIREN not found'}

############################--SOAP--########################3
# Route pour fournir le WSDL
@app.route("/egapro.wsdl", methods=["GET"])
def wsdl():
    return wsdl_template, 200, {'Content-Type': 'text/xml'}

# Route pour le service SOAP
@app.route("/soap", methods=["GET"])
def soap():
    try:

        envelope = etree.fromstring(request.data)
        #Ce base sur ce format XML
        body = envelope.find(".//{http://schemas.xmlsoap.org/soap/envelope/}Body")
        siren_element = body.find(".//siren")
        
        if siren_element is not None:
            siren = siren_element.text
            response_data = egapro_data.get(siren)

            if response_data is None:
                response_xml = """
                <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                        <GetSirenResponse>
                            <error>SIREN not found</error>
                        </GetSirenResponse>
                    </soap:Body>
                </soap:Envelope>
                """
            else:
                #Permet d eviter de renvoyer toute les données en un seul bloc, et les mettre en formes 
                #Ca gere les balises XML de facon dynamique, (si jamais les balises changent)
                response_body_parts = []
                for key, value in response_data.items():
                    ##############################3
                    #Permet de récuper l'en tete du csv et la creer sous forme de balises
                    #Remplacer les espaces et les apostrophes dans les noms de balises
                    tag_name = key.replace(" ", "_").replace("'", "")
                    #Ajouter la balise ouvrante la valeur la balise fermante
                    response_body_parts.append(f"<{tag_name}>{value}</{tag_name}>")
                    #########################33

                #Joindre les parties en une seule chaîne
                response_body = "\n".join(response_body_parts)

                #Mise en forme de la reponse
                response_xml = f"""
                <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                        <GetSirenResponse>
                            {response_body}
                        </GetSirenResponse>
                    </soap:Body>
                </soap:Envelope>
                """
        else:
            #Mise en forme du code erreur si erreur, comme mauvaise methode d'appel
            response_xml = """
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Body>
                    <soap:Fault>
                        <faultcode>SOAP-ENV:Client</faultcode>
                        <faultstring>Invalid request</faultstring>
                    </soap:Fault>
                </soap:Body>
            </soap:Envelope>
            """
        return response_xml, 200, {'Content-Type': 'text/xml'}

    except Exception as e:
        #Mise en forme du code erreur si erreur, comme mauvaise methode d'appel
        return f"""
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <soap:Fault>
                    <faultcode>SOAP-ENV:Server</faultcode>
                    <faultstring>{str(e)}</faultstring>
                </soap:Fault>
            </soap:Body>
        </soap:Envelope>
        """, 500, {'Content-Type': 'text/xml'}

 
if __name__ == '__main__':
    app.run(debug=True)
