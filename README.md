## Sommaire:
- [Installation du serveur de l'API](#installation-du-serveur-de-lapi)
  - [1 . Environnement virtuel et Django](#1--environnement-virtuel-et-django)
  - [2 . Installation des paquets du fichier _requirements.txt_](#2--installation-des-paquets-du-fichier-requirementstxt)
  - [3 . Exécution du serveur](#3--exécution-du-serveur)
  - [4 . Fonctionnement de l'API et documentation](#4--fonctionnement-de-lapi-et-documentation)

# Installation du serveur de l'API

- __Pré-requis : [Python](https://www.python.org/) doit être installé sur votre système__


Tout d'abord, [téléchargez](https://github.com/A-Nourry/P9_LITReview/archive/refs/heads/main.zip) et décompressez le dossier du code avant de passer aux étapes suivantes.

## 1 . Environnement virtuel et Django

Avant de pouvoir exécuter correctement l'API, il faut créer un environnement virtuel.

Pour commencer, ouvrez le terminal,
allez dans le dossier que vous avez téléchargé
(ce n'est pas obligatoire, mais préférable pour vous y retrouver) et tapez la commande suivante :

`python -m venv env`


Exemple :
```
C:\>python -m venv env
```


Cette commande permet de créer l'environnement virtuel **env** et également un dossier **env** dans le répertoire dans lequel vous vous trouvez.

Maintenant que l'environnement virtuel est créé, il faut l'activer. Pour cela tapez la commande suivante :

Mac/Linux: `source env/bin/activate`

Si vous êtes sur Windows il faut exécuter le fichier **activate.bat** qui se trouve dans **env/Scripts/** en tapant directement `env\Scripts\activate.bat`

## 2 . Installation des paquets du fichier _requirements.txt_

Pour que le serveur de l'API puissent correctement s'exécuter, vous aurez besoin d'installer les paquets se trouvant dans le fichier **requirements.txt**


Une fois que l'environnement virtuel est bien activé, assurez-vous d'être dans le dossier que vous avez téléchargé,
là où se trouve le fichier **requirements.txt** et tapez la commande :

`pip install -r requirements.txt`

**_Les paquet Django et Django REST Framework seront installés via le fichier requirements.txt_**

Vous pouvez vérifier que les paquets sont bien installé avec la commande :

`pip freeze`

## 3 . Exécution du serveur

Pour exécuter le serveur de l'API, taper dans le terminal : `python3 manage.py runserver`

Le terminal indiquera que le serveur a bien démarré à l'adresse local [http://127.0.0.1:8000/](http://127.0.0.1:8000/) comme dans l'exemple ci-dessous : 
```
System check identified no issues (0 silenced).
October 03, 2022 - 16:36:10
Django version 4.1.1, using settings 'softdesk.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```
## 4 . Fonctionnement de l'API et documentation

Pour utiliser l'api il suffit maintenant d'ajouter un point de terminaison d'API à la fin de l'adresse [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/).

Exemple : 
`http://127.0.0.1:8000/api/signup/`

Vous trouverez à cette adresse, la documentation de l'API avec tous les points de terminaison disponible : 
[https://documenter.getpostman.com/view/23576713/2s83tGoWr5](https://documenter.getpostman.com/view/23576713/2s83tGoWr5)
