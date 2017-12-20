import sqlite3

SQL_INIT = '''
    CREATE TABLE IF NOT EXISTS info (
        id           INTEGER PRIMARY KEY,
        num_polys    INTEGER,
        num_vertices INTEGER,
        width        INTEGER,
        height       INTEGER,
        creation     DATETIME,
        description  VARCHAR(256),
        reference    BLOB
    );
        
    CREATE TABLE IF NOT EXISTS genotype (
        info_id      INTEGER,
        generation   INTEGER,
        elapsed      FLOAT,
        fitness      FLOAT,
        dna          BLOB,
        FOREIGN KEY(info_id) REFERENCES info(id)
    );
'''
SQL_WRITE_INFO = '''
    INSERT INTO info
    (num_polys, num_vertices, width, height, creation, description, reference)
    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
'''
SQL_WRITE_RESULTS = '''
    INSERT INTO genotype
    (info_id, generation, elapsed, fitness, dna)
    VALUES (?, ?, ?, ?, ?)
'''                    
SQL_READ_ALL_INFO = '''
    SELECT id, num_polys, num_vertices, width, height, creation, description, reference 
    FROM info
    ORDER BY description
'''
SQL_READ_LAST = '''
    SELECT generation, elapsed, fitness, dna FROM genotype ORDER BY ROWID DESC LIMIT 1
'''

class Database:
    def __init__(self, fn):
        self.fn = fn
        self.db = sqlite3.connect(self.fn)
        self.db.row_factory = sqlite3.Row   # provides dict or index access
        self.db.executescript(SQL_INIT)
        
    def writeInfo(self, num_polys, num_vertices, width, height, description, reference):
        cursor = self.db.cursor()
        cursor.execute(SQL_WRITE_INFO,
                       (num_polys, num_vertices, width, height, description, reference))
        self.db.commit()
        return cursor.lastrowid
                      
    def writeResults(self, info_id, generation, elapsed, fitness, dna):
        cursor = self.db.cursor()
        while True:
            cursor.execute(SQL_WRITE_RESULTS,
                           (info_id, generation, elapsed, fitness, dna))
            try:
                self.db.commit()
            except:
                pass
            else:
                break
        return cursor.lastrowid

    def readAllInfo(self):
        cursor = self.db.cursor()
        cursor.execute(SQL_READ_ALL_INFO)
        return cursor.fetchall()
                      
    def readLast(self, info_id):
        cursor = self.db.cursor()
        cursor.execute(SQL_READ_LAST)
        return cursor.fetchone()
        
    def readIndices(self, info_id):
        cursor = self.db.cursor()
        cursor.execute('SELECT ROWID, generation FROM genotype WHERE info_id=?', (info_id,))
        return cursor.fetchall()
        
    def readGenome(self, row_id):
        cursor = self.db.cursor()
        cursor.execute('SELECT elapsed, generation, fitness, dna FROM genotype WHERE ROWID=?', (row_id,))
        return cursor.fetchone()
        
        
    

    