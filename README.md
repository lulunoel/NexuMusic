---

# 🎵 NexuMusic Bot

NexuMusic Bot est un bot Discord multifonctionnel conçu pour offrir des fonctionnalités musicales, de gestion d'invitations et bien plus encore. Ce bot est développé en Python et utilise des bibliothèques telles que `discord.py`.

## 🚀 Fonctionnalités

- **🎶 Commandes musicales :**
  - Lecture de piste radio enregistré une personnel.
  - Gestion de la radio : `!stop`, `!addradio`, `!removeradio`.
  - Commande `!volume` pour régler le volume de la musique.
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
| Commande                | Description                                             |
|-------------------------|---------------------------------------------------------|
| `!radio [radio_name]`   | Affiche la liste des radios ou joue une radio.          |
| `!addradio <name> <url>`| Ajoute une radio personnalisée pour ce serveur.         |
| `!removeradio <name>`   | Retire une radio personnalisée pour ce serveur.         |
| `!stop`                 | Arrête la lecture et vide la file d'attente.            |
| `!volume <0.1-2.0>`     | Règle le volume de la musique.                          |

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
| Commande            | Description                                                       |
|---------------------|-------------------------------------------------------------------|
| `stop`              | Arrête le bot.                                                    |
| `list_guilds`       | Liste les serveurs où le bot est présent.                         |
| `list_members <id>` | Liste les membres d'un serveur spécifique.                        |
| `send_message <id>` | Envoie un message dans un canal spécifique.                       |
| `reload_cog <name>` | Recharge un module (Cog) spécifique.                              |

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
![Licence MIT](https://img.shields.io/badge/License-MIT-blue.svg)

## ✨ Remerciements

- [discord.py](https://discordpy.readthedocs.io/) pour la gestion des interactions Discord.
- [rich](https://github.com/Textualize/rich) pour les améliorations de l'affichage en console.

---
