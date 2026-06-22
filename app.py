import sqlite3
from flask import Flask

def init_db():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimientos(
        
        id INTEGER PRIMARY KEY AUTOINCREMENT,
                   
        nombre TEXT NOT NULL,
                   
        tipo TEXT NOT NULL,
                   
        monto REAL NOT NULL,
                   
        efectivo_ganado REAL DEFAULT 0,
                   
        efectivo_perdido REAL DEFAULT 0,
                   
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    
    conn.commit()
    conn.closet()


app = Flask(__name__)

@app.route("/")
def index():

    return "Hello world!"

if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
