from flask import Flask, render_template, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)

# Configura los detalles de la conexión
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'pythonbiblioteca'
}

# Función para establecer una conexión a la base de datos


def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config, autocommit=True)
    except mysql.connector.Error as e:
        if e.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            # La base de datos no existe, la creamos
            conn = mysql.connector.connect(
                user=db_config['user'],
                password=db_config['password'],
                host=db_config['host']
            )
            cursor = conn.cursor()
            # Creamos la base de datos
            cursor.execute(f"CREATE DATABASE {db_config['database']}")

            # Seleccionamos la base de datos recién creada
            cursor.execute(f"USE {db_config['database']}")

            # Creamos la tabla usuarios si no existe
            cursor.execute("""CREATE TABLE IF NOT EXISTS libro(
                id INT PRIMARY KEY AUTO_INCREMENT,
                titulo VARCHAR(255) NOT NULL,
                autor VARCHAR(255) NOT NULL,
                isbn INT,
                editorial VARCHAR(255),
                ejemplares INT,
                genero VARCHAR(50),
                sinopsis TEXT
                        )""")
            conn.commit()
            cursor.close()
            conn.close()
            # Volvemos a intentar conectarnos después de crear la base de datos
            conn = mysql.connector.connect(**db_config)
        else:
            raise

    return conn


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/registrar_libro', methods=['POST'])
def registrar_libro():
    titulo = request.form.get('titulo')
    autor = request.form.get('autor')
    isbn = request.form.get('isbn')
    editorial = request.form.get('editorial')
    ejemplares = request.form.get('ejemplares')
    genero = request.form.get('genero')
    sinopsis = request.form.get('sinopsis')

    # Insertar datos en la base de datos
    try:
        conn = get_db_connection()
        print("Conexión a la base de datos exitosa")
        cursor = conn.cursor()

        query = "INSERT INTO libro (titulo, autor, isbn, editorial, ejemplares, genero, sinopsis) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (titulo, autor, isbn, editorial, ejemplares, genero, sinopsis)
        cursor.execute(query, values)
        print("Inserción realizada con éxito")
        print(titulo, autor, isbn, editorial, ejemplares, genero, sinopsis)
        conn.commit()
        return """
                Libro registrado exitosamente
            """
    except Exception as e:
        return f"Error al registrar el libro: {str(e)}"
    finally:
        cursor.close()
        conn.close()


@app.route('/libros', methods=['GET'])
def mostrar_libros():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT titulo, autor, ISBN, editorial, ejemplares, genero, sinopsis FROM libro"
        cursor.execute(query)
        libros = cursor.fetchall()
        libros_list = []
        for libro in libros:
            libros_list.append({
                'titulo': libro[0],
                'autor': libro[1],
                'isbn': libro[2],
                'editorial': libro[3],
                'ejemplares': libro[4],
                'genero': libro[5],
                'sinopsis': libro[6]
            })

        cursor.close()
        conn.close()

        return jsonify(libros=libros_list)
    except Exception as e:
        return f"Error al obtener la lista de libros: {str(e)}"
    finally:
        cursor.close()
        conn.close()

# Ruta para editar un libro


@app.route('/editar_libro', methods=['POST'])
def editar_libro():
    isbn_a_editar = request.form.get('nuevo_isbn')
    nuevo_titulo = request.form.get('nuevo_titulo')
    nuevo_autor = request.form.get('nuevo_autor')
    nuevo_isbn = request.form.get('nuevo_isbn')
    nuevo_editorial = request.form.get('nuevo_editorial')
    nuevo_ejemplares = request.form.get('nuevo_ejemplares')
    nuevo_genero = request.form.get('nuevo_genero')
    nueva_sinopsis = request.form.get('nueva_sinopsis')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print("Conexión a la base de datos exitosa")
        print(nuevo_titulo, nuevo_autor, nuevo_isbn, nuevo_editorial, isbn_a_editar,
              nuevo_ejemplares, nuevo_genero, nueva_sinopsis, isbn_a_editar)
        query = "UPDATE libro SET titulo = %s, autor = %s, isbn = %s, editorial = %s, ejemplares = %s, genero = %s, sinopsis = %s WHERE isbn = %s"
        values = (nuevo_titulo, nuevo_autor, nuevo_isbn, nuevo_editorial,
                  nuevo_ejemplares, nuevo_genero, nueva_sinopsis, isbn_a_editar)
        cursor.execute(query, values)
        conn.commit()

        return "Libro editado correctamente"
    except Exception as e:
        return f"Error al editar el libro: {str(e)}"
    finally:
        cursor.close()
        conn.close()


@app.route('/eliminar_libro', methods=['POST'])
def eliminar_libro():
    isbn_a_eliminar = request.form.get('isbn')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "DELETE FROM libro WHERE ISBN = %s"
        values = (isbn_a_eliminar,)
        cursor.execute(query, values)
        conn.commit()

        return "Libro eliminado correctamente"
    except Exception as e:
        return f"Error al eliminar el libro: {str(e)}"
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
