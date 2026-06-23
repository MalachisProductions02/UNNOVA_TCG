import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)




DATABASE = "database.db"

def init_db():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimientos(
        
        id INTEGER PRIMARY KEY AUTOINCREMENT,
                   
        nombre TEXT NOT NULL,
                   
        tipo TEXT NOT NULL,
                   
        efectivo_ganado REAL DEFAULT 0,
                   
        efectivo_gastado REAL DEFAULT 0,
                   
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   
        notas TEXT
        )
        """)
    
    conn.commit()
    conn.close()


def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn

def add_movimiento(
        nombre,
        tipo,
        efectivo_ganado,
        efectivo_gastado
):
    
    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO movimientos
        (
            nombre,
            tipo,
            efectivo_ganado,
            efectivo_gastado
        )
        VALUES (?, ?, ?, ?)
""",
(
    nombre,
    tipo,
    efectivo_ganado,
    efectivo_gastado
))
    
    conn.commit()

    conn.close()


def get_movimientos():

    conn = get_db()

    movimientos = conn.execute(""" 
        SELECT *
        FROM movimientos
        ORDER BY fecha DESC
    """).fetchall()

    conn.close()

    return movimientos

def get_totales():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(""" 
        SELECT
            COALESCE(SUM(efectivo_ganado),0),
            COALESCE(SUM(efectivo_gastado),0)
        FROM movimientos
    """)

    resultado = cursor.fetchone()

    conn.close()

    dinero_guardado = resultado[0]

    dinero_gastado = resultado[1]

    ganancias = dinero_guardado - dinero_gastado

    return {
        "ganancias": ganancias,
        "guardado": dinero_guardado,
        "gastado": dinero_gastado
    }



if __name__ == "__main__":
    print(os.path.abspath(DATABASE))

    init_db()

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(movimientos)")
    
    print(cursor.fetchall())

    conn.close()

    add_movimiento(
    "Lote Cartas Vualá",
    "Venta",
    100,
    0
    )

    add_movimiento(
    "Chandeleur",
    "Venta",
    50,
    0
    )

    add_movimiento(
    "Zacian EX",
    "Venta",
    10,
    0
    )

    add_movimiento(
    "Mesa Plaza Fiesta",
    "Gasto",
    0,
    150
    )

    print(get_totales())


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )


@app.route("/")
def index():

    return "Hello world!"

@app.route("/add")
def add():

    return render_template("add_movement.html")
