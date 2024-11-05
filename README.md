# Implémentation d'une messagerie sécurisée

Rodrigue LAZARUS & Rémy TANG

## Tâches effectuées

### 02/10/24 - 09/10/24

- Première rencontre avec l'encadrant projet.
- Lecture du papier de Boneh & Franklin.
- Création de l'environnement de développement.
- Exécution d'une implémentation fournie sous notebook Jupyter.

### 09/10/24 - 16/10/24

- Tests d'envoi de messages S/MIME

### 16/10/24 - 23/10/24

- Tests d'une implémentation IBE basée sur le papier de Boneh & Franklin.

### 23/10/24 - 30/10/24

Implémentation d'une application tournant en local pour montrer l'utilisation de l'IBE dans un contexte de messagerie.

Cas d'utilisation :
- Envoi d'un message encrypté à un destinataire n'ayant pas encore créé son compte.
- Envoi de deux messages identiques pour montrer que le ciphertext change grâce au tirage aléatoire.

## Installation

```bash
conda env create --name pesto-crypto --file=environment.yml
conda activate pesto-crypto
```

## Lancer l'application en local

Le sous-package `cypari2`, utilisé par s`age` pour toutes les opérations sur les grands nombres, n'est pas *thread-safe* et pose des problèmes avec Flask par défaut. On doit donc lancer l'application avec 1 thread et 1 worker.

```bash
cd app
gunicorn --workers 1 --threads 1 ibemail:create_app()
```