---

# 🎵 NexuMusic Bot

NexuMusic Bot est un bot Discord multifonctionnel conçu pour offrir des fonctionnalités musicales, de gestion d'invitations et bien plus encore. Ce bot est développé en Python et utilise des bibliothèques telles que `discord.py`.

## Technologies Utilisées

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL">
  <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord">
  <img src="https://img.shields.io/badge/MIT_License-blue?style=for-the-badge&logo=open-source-initiative&logoColor=white" alt="MIT License">
</p>

## 🚀 Fonctionnalités

- **🎶 Commandes musicales :**
  - Lecture de piste radio enregistré une personnel.
  - Gestion de la music : `!play`, `!pause`, `!resume`.
  - Gestion de la radio : `!stop`, `!addradio`, `!removeradio`.
  - Commande `!volume` pour régler le volume de la radio.
  - Commande `!queue` pour voir le liste d'atente.
- **📨 Gestion des invitations :**
  - Suivi des invitations créées et utilisées.
  - Commande pour voir qui a invité un utilisateur : `!who_invited`.
  - Commande pour voir combien d'invitations un utilisateur a : `!invite_count`.
  - Suivi des départs et des retours des membres.
- **⚙ Setup :**
  - Gestion de la configuration de votre serveur.
  - Différente commande de configuration : `!setlogchannel`, `setcountchannel`, `setwelcomechannel`.
- **💼 Serveur :**
  - Affichage d'information propre au serveur.
  - Commande pour voir les informations : `!serverinfo`.
- **🖥️ Commandes console :**
  - Gestion avancée via une interface console stylisée (liste des serveurs, envoi de messages, rechargement de Cogs).
- **📋 Intégration MySQL :**
  - Sauvegarde des données liées aux invitations et aux serveurs.

## 🛠️ Installation

### Prérequis

- Python 3.8 ou supérieur.
- Une base de données MySQL.

### Étapes

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/lulunoel/NexuMusic.git
   cd votre-repo
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Configurez un fichier `.env` à la racine du projet :
   ```env
   TOKEN=Votre_Token_Discord
   HOST=localhost
   UTILISATEUR=root
   PASSWORD=votre_mot_de_passe
   DATABASE=nexumusic
   PORT=3306
   SECRET=client_secret spotify
   CLIENT=client_id spotify
   ```

4. Configurez la base de données MySQL :
   - Créez les tables nécessaires avec les scripts dans le fichier `database.py`.
   - Exemple :
     ```sql
     CREATE TABLE invites (
         id INT AUTO_INCREMENT PRIMARY KEY,
         invite_code VARCHAR(255) UNIQUE NOT NULL,
         inviter_id BIGINT NOT NULL,
         guild_id BIGINT NOT NULL,
         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
     );

     CREATE TABLE invite_uses (
         id INT AUTO_INCREMENT PRIMARY KEY,
         user_id BIGINT NOT NULL,
         invite_code VARCHAR(255) NOT NULL,
         guild_id BIGINT NOT NULL,
         used_at DATETIME DEFAULT CURRENT_TIMESTAMP
     );
     ```

5. Lancez le bot :
   ```bash
   python bot.py
   ```

## 📜 Commandes

### 🎶 Musique
| Commande                | Description                                                         |
|-------------------------|---------------------------------------------------------------------|
| `!radio [radio_name]`   | Affiche la liste des radios ou joue une radio.                      |
| `!addradio <name> <url>`| Ajoute une radio personnalisée pour ce serveur.                     |
| `!removeradio <name>`   | Retire une radio personnalisée pour ce serveur.                     |
| `!stop`                 | Arrête la lecture et vide la file d'attente.                        |
| `!volume <0.1-2.0>`     | Règle le volume de la musique de la radio.                          |
| `!pause`                | Met en pause la lecture en cours.                                   |
| `!play <url>`           | Joue une musique depuis une URL YouTube ou Spotify.                 |
| `!playlist <url>`       | Affiche les vidéos d'une playlist YouTube avec option Play All.     |
| `!queue`                | Affiche la file d'attente des musiques.                             |
| `!resume`               | Reprend la lecture mise en pause.                                   |
| `!skip`                 | Passe à la prochaine musique dans la file d'attente.                |
| `!skipto <index>`       | Saute à une chanson spécifique dans la file d'attente.              |

### 📨 Invitations
| Commande              | Description                                                       |
|-----------------------|-------------------------------------------------------------------|
| `!who_invited <user>` | Montre qui a invité l'utilisateur.                                |
| `!invite_count <user>`| Affiche le nombre de personnes invitées par l'utilisateur.        |
| `!invitations`        | Liste toutes les invitations actives sur le serveur.              |

### ⚙ Setup
| Commande                      | Description                                                       |
|-------------------------------|-------------------------------------------------------------------|
| `!setcountchannel <channel>`  | Définit ou met à jour le canal de conteur pour le serveur.        |
| `!setlogchannel <channel>`    | Définit ou met à jour le canal de logs pour le serveur.           |
| `!setwelcomechannel <channel>`| Définit ou met à jour le canal de bienvenue pour le serveur.      |

### 💼 Serveur
| Commande       | Description                                 |
|----------------|---------------------------------------------|
| `!serverinfo`  | Affiche les informations du serveur.        |


### 🖥️ Console
| Commande                              | Description                                                       |
|---------------------------------------|-------------------------------------------------------------------|
| `stop`                                | Arrête le bot.                                                    |
| `list_guilds`                         | Liste les serveurs où le bot est présent.                         |
| `list_members <id>`                   | Liste les membres d'un serveur spécifique.                        |
| `send_message <id>`                   | Envoie un message dans un canal spécifique.                       |
| `list_channels <guild_id>`            | Affiche la liste des canaux d'un serveur spécifique.              |
| `send_message <channel_id> <message>` | Envoie un message dans un canal spécifique.                       |
| `reload_cog <name>`                   | Recharge un module (Cog) spécifique.                              |
| `leave_guild <guild_id>`              | Fait quitter un serveur au bot.                                   |
| `create_invite <guild_id>`            | Crée une invitation pour un serveur spécifique.                   |

## 🖼️ Exemple d'Interface Console

```plaintext
> list_guilds
╔═══════════════════════╤═══════════════════╗
║ Nom du Serveur        │ ID                ║
╟───────────────────────┼───────────────────╢
║ MonServeur            │ 123456789012345678║
╚═══════════════════════╧═══════════════════╝
```

## 🤝 Contributions

Les contributions sont les bienvenues ! N'hésitez pas à proposer des améliorations, signaler des bugs ou ajouter de nouvelles fonctionnalités.

1. Forkez ce dépôt.
2. Créez une branche pour votre fonctionnalité : `git checkout -b ma-fonctionnalite`.
3. Faites vos modifications et testez-les.
4. Poussez la branche : `git push origin ma-fonctionnalite`.
5. Créez une Pull Request.

## 📄 Licence

Ce projet est sous licence [MIT](LICENSE).

## ✨ Remerciements

- [discord.py](https://discordpy.readthedocs.io/) pour la gestion des interactions Discord.
- [rich](https://github.com/Textualize/rich) pour les améliorations de l'affichage en console.

---
