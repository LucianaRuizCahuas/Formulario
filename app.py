import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# No cargamos .env aquí si las variables se setean en supervisor
# load_dotenv()

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

app.secret_key = 'una_clave_secreta_muy_segura_para_produccion' # ¡CAMBIA ESTO EN PRODUCCIÓN!

# Las variables de entorno serán inyectadas por Supervisor
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT', 3306)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=int(DB_PORT)
        )
        if conn.is_connected():
            print(f"Conexión a la base de datos exitosa: {DB_NAME} en {DB_HOST}")
        return conn
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        mensaje = request.form['mensaje']

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                sql = "INSERT INTO contactos (nombre, email, mensaje) VALUES (%s, %s, %s)"
                val = (nombre, email, mensaje)
                cursor.execute(sql, val)
                conn.commit()
                cursor.close()
                flash('¡Tu mensaje ha sido enviado con éxito!', 'success')
                return redirect(url_for('index'))
            except Error as e:
                print(f"Error al guardar el mensaje en la base de datos: {e}")
                flash(f'Error al enviar el mensaje: {e}', 'error')
                return redirect(url_for('index'))
            finally:
                conn.close()
        else:
            flash('No se pudo conectar a la base de datos. Inténtalo de nuevo más tarde.', 'error')
            return redirect(url_for('index'))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
