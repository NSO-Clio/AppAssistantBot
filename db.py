import sqlite3

class UserDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Создание таблицы пользователей, если она не существует
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            question TEXT,
            answer TEXT,
            topic TEXT DEFAULT NULL, 
            grade INTEGER DEFAULT 2 
        )''')
        self.conn.commit()

    def add_question(self, telegram_id, question, topic, answer, quality):
        try:
            self.cursor.execute('''INSERT INTO users (telegram_id, question, answer, topic, grade) 
                                   VALUES (?, ?, ?, ?, ?)''',
                                (telegram_id, question, answer, topic, quality))
            self.conn.commit()
        except Exception as e:
            print(f"Error while adding question: {e}")

    def get_all_data(self):
        self.cursor.execute("SELECT * FROM users")
        users = self.cursor.fetchall()
        return users

    def close(self):
        self.conn.close()

    # Context manager methods
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
