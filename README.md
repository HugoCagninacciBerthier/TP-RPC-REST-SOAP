# Documentation des API (REST, SOAP et JSON-RPC)

## Introduction

Fais par : Arnaud.G, Celia.M, Hugo.C

Ce projet implémente trois API (REST, SOAP et RPC) permettant de rechercher des entreprises par leur numéro SIREN à partir d'un fichier CSV contenant des données sur les entreprises.
Les API sont implémentées en Python avec Flask et Flask-RESTx pour l'API REST, Flask avec Zeep pour l'API SOAP, et Flask avec Flask-JSONRPC pour l'API JSON-RPC.

## Prérequis

- Python 3.x
- Flask
- Flask-RESTx
- pandas
- Zeep
- lxml
- Flask-JSONRPC

**Vous devez installer les dépendances avec la commande :**

```
pip install flask flask-restx pandas zeep lxml flask-jsonrpc
```

## 1\. API REST

### Fonctionnalité

L'API permet d'obtenir des informations sur une entreprise à partir de son numéro SIREN.

### Chercher une entreprise par son SIREN

```
- GET /siren/<siren_id> : Recherche une entreprise par son numéro SIREN.
```

### Paramètres

- **Entrée** : siren_id (string) - Numéro SIREN de l'entreprise recherchée.
- **Sortie** : JSON contenant les informations de l'entreprise ou un message d'erreur si le SIREN n'est pas trouvé.

### Utilisation

Vous pouvez utiliser POSTMAN pour effectuer cette requête HTTP GET.
Ou dans le navigateur web, et faire une requete HTTP GET tel que http://localhost:5000/siren/<siren>

#### Requête

```
curl -X GET "http://localhost:5000/siren/123456789"
```

#### Réponse

```
{
    "Année": "2023",
    "Structure": "Entreprise XYZ",
    "Tranche d'effectifs": "50-99",
    "SIREN": "123456789",
    "Raison Sociale": "XYZ SAS",
    "Région": "Île-de-France",
    "Département": "75",
    "Pays": "France",
    "Code NAF": "6201Z",
    "Note Index": "85"
}
```

### Lancement du serveur

```
python API_REST.py
```

Par défaut, l'API sera disponible à l'adresse http://localhost:5000 ou 127.0.0.1:5000.

## 2\. API SOAP

### Fonctionnalité

L'API SOAP permet de récupérer les mêmes informations qu'avec l'API REST, mais en utilisant le protocole SOAP qui est basé sur le XML.

### Paramètres

- **Entrée** : siren (string) - Numéro SIREN de l'entreprise recherchée.
- **Sortie** : XML contenant les informations de l'entreprise ou un message d'erreur si le SIREN n'est pas trouvé.

### Exemple d'utilisation

Pour executer une requette HTTP GET, il faudra utiliser Postman, et précisé dans l'entete le Content-Type : text/xml et dans le body en RAW XML la requete ci-dessous.

#### Requête SOAP (XML)

```
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <GetSiren>
            <siren>123456789</siren>
        </GetSiren>
    </soap:Body>
</soap:Envelope>
```

#### Exemple de réponse SOAP (XML)

```
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetSirenResponse>
      <Année>2023</Année>
      <Structure>Entreprise XYZ</Structure>
      <Tranche_deffectifs>50-99</Tranche_deffectifs>
      <SIREN>123456789</SIREN>
      <Raison_Sociale>XYZ SAS</Raison_Sociale>
      <Région>Île-de-France</Région>
      <Département>75</Département>
      <Pays>France</Pays>
      <Code_NAF>6201Z</Code_NAF>
      <Note_Index>85</Note_Index>
    </GetSirenResponse>
  </soap:Body>
</soap:Envelope>
```

### Lancement du serveur

```
python API_SOAP.py
```

L'API sera disponible à l'adresse http://localhost:5000.

## 3\. API JSON-RPC

### Fonctionnalité

L'API JSON-RPC permet de rechercher une entreprise par son numéro SIREN et de retourner les informations les plus récentes.

### Installation et mise en place

Pour exécuter cette API, vous devez avoir Flask et Flask-JSONRPC installés.

1. Installer les dépendances :

```
pip install flask flask-jsonrpc pandas
```

2. Lancer le serveur JSON-RPC :

```
python egapro-api-rpc.py
```

Par défaut, l'API sera disponible à l'adresse http://localhost:5000/api.

### Appel de l'API

Pour generer une requette HTTP, il faudra utiliser Postman, dans l'entete de fichier mettre le Content-Type à "application/json", puis dans le body en RAW JSON, la requete.
Vous pouvez effectuer un appel JSON-RPC en envoyant une requête POST au point d'entrée `/api` avec le format suivant :

#### Requête

```
{
    "jsonrpc": "2.0",
    "method": "api.search_by_siren",
    "params": {"siren": "501615355"},
    "id": 1
}
```

#### Réponse

```
{
    "id": 1,
    "jsonrpc": "2.0",
    "result": {
        "Année": 2023,
        "Code NAF": "59.12Z - Post-production de films cinématographiques, de vidéo et de programmes de télévision",
        "Département": "Paris",
        "Entreprises UES (SIREN)": "OCS (539311373),ORANGE STUDIO (440419240)",
        "Nom UES": "UES OCS OPTV OS",
        "Note Ecart rémunération": "39",
        "Note Ecart taux d'augmentation": "35",
        "Note Ecart taux d'augmentation (hors promotion)": NaN,
        "Note Ecart taux de promotion": NaN,
        "Note Hautes rémunérations": "10",
        "Note Index": "99",
        "Note Retour congé maternité": "15",
        "Pays": "FRANCE",
        "Raison Sociale": "ORANGE PRESTATIONS TV",
        "Région": "Île-de-France",
        "SIREN": "501615355",
        "Structure": "Unité Economique et Sociale (UES)",
        "Tranche d'effectifs": "50 à 250"
    }
}
```

L'API retourne les informations les plus récentes disponibles pour le SIREN recherché.


