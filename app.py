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
        efectivo_gastado,
        notas
):
    
    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO movimientos
        (
            nombre,
            tipo,
            efectivo_ganado,
            efectivo_gastado,
            notas
        )
        VALUES (?, ?, ?, ?, ?)
""",
(
    nombre,
    tipo,
    efectivo_ganado,
    efectivo_gastado,
    notas
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


@app.route("/")
def index():

    tipo = request.args.get("tipo")
    min_monto = request.args.get("min")
    max_monto = request.args.get("max")
    search = request.args.get("q")

    query = "SELECT * FROM movimientos WHERE 1=1"
    params = []

    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)

    if min_monto:
        query += " AND (efectivo_ganado + efectivo_gastado) >= ?"
        params.append(min_monto)

    if max_monto:
        query += " AND (efectivo_ganado + efectivo_gastado) <= ?"
        params.append(max_monto)

    if search:
        query += " AND (nombre LIKE ? OR notas LIKE ?)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    query += " ORDER BY fecha DESC"

    conn = get_db()
    movimientos = conn.execute(query, params).fetchall()
    conn.close()

    totales = get_totales()
    movimientos = get_movimientos()

    return render_template(
        "index.html",
        totales=totales,
        movimientos=movimientos
    )

@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":

        nombre = request.form["nombre"]
        tipo = request.form["tipo"]
        ganancia = float(request.form["efectivo_ganado"] or 0)
        gasto = float(request.form["efectivo_gastado"] or 0)
        notas = request.form.get("notas", "")


        add_movimiento(
            nombre,
            tipo,
            ganancia,
            gasto,
            notas
        )

        return redirect(url_for("index"))
    return render_template("add_movement.htm")


@app.route("/search", methods=["GET", "POST"])
def search():

    resultados = []

    if request.method == "POST":
        q = request.form.get("q", "")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(""" 
            SELECT *
            FROM movimientos
            WHERE nombre LIKE ?
            OR tipo LIKE ?
            OR notas LIKE ?
            ORDER BY fecha DESC
        """, (f"%{q}%", f"%{q}%", f"%{q}%"))

        resultados = cursor.fetchall()
        conn.close()

    return render_template("search.html", resultados=resultados)


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
    0,
    "Venta del Sábado (Monto de Prueba)"
    )

    add_movimiento(
    "Chandeleur",
    "Venta",
    50,
    0,
    "Venta del Sábado (Monto de Prueba)"
    )

    add_movimiento(
    "Zacian EX",
    "Venta",
    10,
    0,
    "Venta del Sábado (Monto de Prueba)"
    )

    add_movimiento(
    "Mesa Plaza Fiesta",
    "Gasto",
    0,
    150,
    "Gasto de esta semana (Monto de Prueba)"
    )

    print(get_totales())


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )


