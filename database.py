import pymysql
from console_config import setup_console  

logger = setup_console('database')


class Database:
    def __init__(self, host, user, password, database, port):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port

    def connect(self):
        try:
            return pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                port=int(self.port)
            )
        except pymysql.MySQLError as e:
            logger.error(f"Failed to connect to MySQL server: {e}")
            raise Exception(f"Failed to connect to MySQL server: {e}")
            
    def setup_database(self):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS server_settings (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        server_id BIGINT UNIQUE NOT NULL,
                        server_name VARCHAR(255) NOT NULL,
                        volume FLOAT DEFAULT 1.0,
                        last_radio VARCHAR(255) DEFAULT NULL,
                        server_log_id BIGINT UNIQUE NULL,
                        server_welcome_id BIGINT UNIQUE NULL,
                        server_count_id BIGINT UNIQUE NULL,
                        server_suggestion_id BIGINT UNIQUE NULL
                    )
                """)
                connection.commit()
                
    def setup_reactions_database(self):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS message_reactions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        message_id BIGINT NOT NULL,
                        user_id BIGINT NOT NULL,
                        reaction_type VARCHAR(10) NOT NULL,
                        reacted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NULL,
                        channel_id BIGINT NOT NULL,
                        is_active BIGINT NOT NULL DEFAULT 1,
                        UNIQUE (message_id, user_id)
                    )
        		""")
                connection.commit()

    def setup_economy_database(self):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS economy (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        guild_id VARCHAR(255) NOT NULL,
                        points INT DEFAULT 0,
                        UNIQUE KEY unique_user_guild (user_id, guild_id)
                    )
        		""")
                connection.commit()
                
    def setup_daily_rewards_database(self):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS daily_rewards (
                        user_id BIGINT NOT NULL,
                        last_claimed TIMESTAMP NOT NULL,
                        PRIMARY KEY (user_id)
                    )
        		""")
                connection.commit()
                
    def setup_invites_database(self):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS invite_uses (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id BIGINT NOT NULL,                -- ID de l'utilisateur ayant rejoint
                        invite_code VARCHAR(255) NOT NULL,      -- Code de l'invitation utilisée
                        guild_id BIGINT NOT NULL,               -- ID du serveur où l'utilisateur a rejoint
                        used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Date d'utilisation de l'invitation
                        FOREIGN KEY (invite_code) REFERENCES invites(invite_code) ON DELETE CASCADE
                    )
        		""")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS invites (
                        invite_code VARCHAR(255) PRIMARY KEY,   -- Code unique de l'invitation
                        inviter_id BIGINT NOT NULL,             -- ID de l'utilisateur ayant créé l'invitation
                        guild_id BIGINT NOT NULL,               -- ID du serveur où l'invitation a été créée
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Date de création de l'invitation
                    )
        		""")
                connection.commit()
                
    def setup_radio_database(self):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS custom_radios (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        server_id BIGINT NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        url TEXT NOT NULL,
                        UNIQUE (server_id, name)
                    )
        		""")
                connection.commit()

    def get_server_settings(self, server_id):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM server_settings WHERE server_id = %s", (server_id,))
                return cursor.fetchone()

    def upsert_server_settings(self, server_id, server_name, volume, last_radio):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO server_settings (server_id, server_name, volume, last_radio)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    server_name = VALUES(server_name),
                    volume = VALUES(volume),
                    last_radio = VALUES(last_radio)
                """, (server_id, server_name, volume, last_radio))
                connection.commit()

    def add_custom_radio(self, server_id, name, url):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute("INSERT INTO custom_radios (server_id, name, url) VALUES (%s, %s, %s)", (server_id, name, url))
                    connection.commit()
                    return True
                except pymysql.IntegrityError:
                    return False  
        
    def remove_custom_radio(self, server_id, name):
        """Retire une radio personnalisée pour un serveur."""
        with self.connect() as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute("DELETE FROM custom_radios WHERE server_id = %s AND name = %s", (server_id, name))
                    connection.commit()
                    return cursor.rowcount > 0 
                except Exception as e:
                    print(f"[ERREUR] Suppression de la radio échouée : {e}")
                    return False

    def get_custom_radios(self, server_id):
        """Récupère toutes les radios personnalisées d'un serveur."""
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name, url FROM custom_radios WHERE server_id = %s", (server_id,))
                return cursor.fetchall()

    def add_reaction(self, message_id, channel_id, user_id, reaction_type, is_active=True):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM message_reactions WHERE message_id = %s AND user_id = %s", (message_id, user_id))
                result = cursor.fetchone()
                if result:
                    cursor.execute("UPDATE message_reactions SET reaction_type = %s, is_active = %s WHERE message_id = %s AND user_id = %s", (reaction_type, is_active, message_id, user_id))
                else:
                    cursor.execute("INSERT INTO message_reactions (message_id, channel_id, user_id, reaction_type, is_active) VALUES (%s, %s, %s, %s, %s)", (message_id, channel_id, user_id, reaction_type, is_active))
                connection.commit()

    def deactivate_reaction(self, message_id):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE message_reactions SET is_active = 0 WHERE message_id = %s", (message_id,))
                connection.commit()

    def get_reaction_counts(self, message_id):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT reaction_type, COUNT(*) AS count FROM message_reactions WHERE message_id = %s AND is_active = 1 GROUP BY reaction_type", (message_id,))
                results = cursor.fetchall()
                return {result['reaction_type']: result['count'] for result in results}

    def count_reactions(self, message_id):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT reaction_type, COUNT(*) as count FROM message_reactions WHERE message_id = %s GROUP BY reaction_type", (message_id,))
                results = cursor.fetchall()
                return {row['reaction_type']: row['count'] for row in results}

    def user_already_reacted(self, message_id, user_id):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM message_reactions WHERE message_id = %s AND user_id = %s", (message_id, user_id))
                return cursor.fetchone() is not None

    def get_points(self, user_id, guild_id):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT points FROM economy WHERE user_id = %s AND guild_id = %s", (user_id, guild_id))
                result = cursor.fetchone()
                return result['points'] if result else 0

    def add_points(self, user_id, guild_id, amount):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO economy (user_id, guild_id, points) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE points = points + %s", (user_id, guild_id, amount, amount))
                connection.commit()
                
    def set_points(self, user_id, guild_id, points):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO economy (user_id, guild_id, points) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE points = %s", (user_id, guild_id, points, points))
                connection.commit()

    def remove_points(self, user_id, guild_id, amount):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE economy SET points = GREATEST(0, points - %s) WHERE user_id = %s AND guild_id = %s", (amount, user_id, guild_id))
                connection.commit()
                
    def get_user_position(self, user_id, guild_id):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                query = """
                SELECT rank FROM (
                    SELECT user_id, guild_id, points, RANK() OVER (ORDER BY points DESC) AS rank
                    FROM economy WHERE guild_id = %s
                ) AS ranked WHERE user_id = %s
                """
                cursor.execute(query, (guild_id, user_id))
                result = cursor.fetchone()
                return result['rank'] if result else None
            
    def get_leaderboard(self, guild_id, limit=10, offset=0):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT user_id, points FROM economy
                    WHERE guild_id = %s
                    ORDER BY points DESC
                    LIMIT %s OFFSET %s
                """, (guild_id, limit, offset))
                return cursor.fetchall()
            
    def get_total_entries(self, guild_id):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM economy WHERE guild_id = %s", (guild_id,))
                result = cursor.fetchone()
                return result['COUNT(*)'] if result else 0
            
    def get_last_claimed(self, user_id):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT last_claimed FROM daily_rewards WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                return result['last_claimed'] if result else None

    def update_last_claimed(self, user_id):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                INSERT INTO daily_rewards (user_id, last_claimed)
                VALUES (%s, CURRENT_TIMESTAMP)
                ON DUPLICATE KEY UPDATE last_claimed = CURRENT_TIMESTAMP
                """, (user_id,))
                connection.commit()
                
    def get_invite_count(self, user_id, guild_id):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                SELECT COUNT(*) AS invite_count FROM invite_uses iu
                JOIN invites i ON iu.invite_code = i.invite_code
                WHERE i.inviter_id = %s AND i.guild_id = %s;
                """, (user_id, guild_id))
                result = cursor.fetchone()
                return result['invite_count'] if result else 0
            
    def set_log_channel(self, server_id, server_log_id):
        try:
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE server_settings SET server_log_id = %s WHERE server_id = %s", (server_log_id, server_id))
                    connection.commit()
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du canal de log pour le serveur {server_id}: {e}")
            
    def set_welcome_channel(self, server_id, server_welcome_id):
        try:
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE server_settings SET server_welcome_id = %s WHERE server_id = %s", (server_welcome_id, server_id))
                    connection.commit()
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du canal de log pour le serveur {server_id}: {e}")
            
    def set_count_channel(self, server_id, server_count_id):
        try:
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE server_settings SET server_count_id = %s WHERE server_id = %s", (server_count_id, server_id))
                    connection.commit()
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du canal de log pour le serveur {server_id}: {e}")
            
    def set_suggestion_channel(self, server_id, server_suggestion_id):
        try:
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE server_settings SET server_suggestion_id = %s WHERE server_id = %s", (server_suggestion_id, server_id))
                    connection.commit()
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du canal de log pour le serveur {server_id}: {e}")
            
    def set_invite_table(self, invite_code, inviter_id, guild_id):
        try:
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    sql = """
                    INSERT INTO invites (invite_code, inviter_id, guild_id)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE inviter_id = VALUES(inviter_id)
                    """
                    cursor.execute(sql, (invite_code, inviter_id, guild_id))
                    connection.commit()
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'invitation pour le serveur {guild_id}: {e}")
            
        def check_invite_used(self, user_id, invite_code, guild_id):
            query = """
            SELECT COUNT(*) as count
            FROM invite_uses
            WHERE user_id = %s AND invite_code = %s AND guild_id = %s
            """
            self.cursor.execute(query, (user_id, invite_code, guild_id))
            return self.cursor.fetchone()

        def add_invite_use(self, user_id, invite_code, guild_id):
            self.cursor.execute(
                """
                INSERT INTO invite_uses (user_id, invite_code, guild_id)
                VALUES (%s, %s, %s)
                """,
                (user_id, invite_code, guild_id)
            )
            self.connection.commit()
            
        def get_invite_info_on_member_leave(self, user_id, guild_id):
            query = """
            SELECT iu.invite_code, i.inviter_id 
            FROM invite_uses iu
            JOIN invites i ON iu.invite_code = i.invite_code
            WHERE iu.user_id = %s AND iu.guild_id = %s
            """
            self.cursor.execute(query, (user_id, guild_id))
        return self.cursor.fetchone()
