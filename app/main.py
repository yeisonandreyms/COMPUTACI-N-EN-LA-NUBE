from fastapi import FastAPI, Request
import os
import psycopg2

app = FastAPI()
DATA_FILE = "/data/notas.txt"

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"), 
        password=os.getenv("DB_PASS"), 
        port="5432"
    )

@app.post("/nota")
async def guardar_nota(request: Request):
    nota = await request.body()
    nota_texto = nota.decode()

    with open(DATA_FILE, "a") as f:
        f.write(nota_texto + "\n")
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO notas (contenido) VALUES (%s)", (nota_texto,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return {"error": str(e)}

    return {"mensaje": "Nota guardada en archivo y base de datos"}

@app.get("/")
def leer_notas():
    if not os.path.exists(DATA_FILE):
        return {"notas": []}
    with open(DATA_FILE, "r") as f:
        return {"notas": f.read().splitlines()}

@app.get("/conteo")
def contar_notas():
    if not os.path.exists(DATA_FILE):
        return {"cantidad": 0}
    with open(DATA_FILE, "r") as f:
        lineas = f.readlines()
        return {"cantidad": len(lineas)}

@app.get("/notas-db")
def obtener_notas_db():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, contenido FROM notas")
        notas = [{"id": row[0], "contenido": row[1]} for row in cur.fetchall()]
        cur.close()
        conn.close()
        return {"notas": notas}
    except Exception as e:
        return {"error": str(e)}

@app.get("/autor")
def obtener_autor():
    autor = os.getenv("AUTOR", "Desconocido")
    return {"autor": autor}
