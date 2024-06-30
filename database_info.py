import sqlite3

class DatabaseInfo:
    @staticmethod
    def get_db_info(db_path, file_name):
        conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        c = conn.cursor()
        c.execute('PRAGMA integrity_check')
        if c.fetchone()[0] != 'ok':
            raise Exception("Database integrity check failed")
        c.execute('SELECT Z_PK, ZDURATION, ZDATE, ZAUDIODIGEST, ZUNIQUEID FROM ZCLOUDRECORDING WHERE ZPATH LIKE ?', (f'%{file_name}',))
        return c.fetchone()
