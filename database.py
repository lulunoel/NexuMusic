import pymysql

class Database:
    def __init__(self, host, user, password, database, port):
        self.connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            port=int(port)
        )
        self.cursor = self.connection.cursor()

    def setup_database(self):
        """Crée les tables nécessaires si elles n'existent pas."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS server_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            server_id BIGINT UNIQUE NOT NULL,
            server_name VARCHAR(255) NOT NULL,
            volume FLOAT DEFAULT 1.0,
            last_radio VARCHAR(255) DEFAULT NULL,
            server_log_id BIGINT UNIQUE NULL,
            server_welcome_id BIGINT UNIQUE NULL,
            server_count_id BIGINT UNIQUE NULL
        )
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()
        
    def setup_invites_database(self):
        """Crée les tables nécessaires pour la gestion des invitations."""
        create_invites_table = """
        CREATE TABLE IF NOT EXISTS invites (
            invite_code VARCHAR(255) PRIMARY KEY,   -- Code unique de l'invitation
            inviter_id BIGINT NOT NULL,             -- ID de l'utilisateur ayant créé l'invitation
            guild_id BIGINT NOT NULL,               -- ID du serveur où l'invitation a été créée
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Date de création de l'invitation
        )
        """
        create_invite_uses_table = """
        CREATE TABLE IF NOT EXISTS invite_uses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT NOT NULL,                -- ID de l'utilisateur ayant rejoint
            invite_code VARCHAR(255) NOT NULL,      -- Code de l'invitation utilisée
            guild_id BIGINT NOT NULL,               -- ID du serveur où l'utilisateur a rejoint
            used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Date d'utilisation de l'invitation
            FOREIGN KEY (invite_code) REFERENCES invites(invite_code) ON DELETE CASCADE
        )
        """
        self.cursor.execute(create_invites_table)
        self.cursor.execute(create_invite_uses_table)
        self.connection.commit()

    def setup_radio_database(self):
        """Crée les tables nécessaires si elles n'existent pas."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS custom_radios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            server_id BIGINT NOT NULL,
            name VARCHAR(255) NOT NULL,
            url TEXT NOT NULL,
            UNIQUE (server_id, name)
        )
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def get_server_settings(self, server_id):
        """Récupère les paramètres d'un serveur."""
        query = "SELECT * FROM server_settings WHERE server_id = %s"
        self.cursor.execute(query, (server_id,))
        return self.cursor.fetchone()

    def upsert_server_settings(self, server_id, server_name, volume, last_radio):
        """Insère ou met à jour les paramètres d'un serveur."""
        query = """
        INSERT INTO server_settings (server_id, server_name, volume, last_radio)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        server_name = VALUES(server_name),
        volume = VALUES(volume),
        last_radio = VALUES(last_radio)
        """
        self.cursor.execute(query, (server_id, server_name, volume, last_radio))
        self.connection.commit()

    def add_custom_radio(self, server_id, name, url):
        """Ajoute une radio personnalisée pour un serveur."""
        query = """
        INSERT INTO custom_radios (server_id, name, url)
        VALUES (%s, %s, %s)
        """
        try:
            self.cursor.execute(query, (server_id, name, url))
            self.connection.commit()
            return True
        except pymysql.IntegrityError:
            return False  
        
    def remove_custom_radio(self, server_id, name):
        """Retire une radio personnalisée pour un serveur."""
        query = """
        DELETE FROM custom_radios
        WHERE server_id = %s AND name = %s
        """
        try:
            self.cursor.execute(query, (server_id, name))
            self.connection.commit()
            return self.cursor.rowcount > 0 
        except Exception as e:
            print(f"[ERREUR] Suppression de la radio échouée : {e}")
            return False

    def get_custom_radios(self, server_id):
        """Récupère toutes les radios personnalisées d'un serveur."""
        query = "SELECT name, url FROM custom_radios WHERE server_id = %s"
        self.cursor.execute(query, (server_id,))
        return self.cursor.fetchall()
    
    def close(self):
        """Ferme la connexion à la base de données."""
        self.cursor.close()
        self.connection.close()
