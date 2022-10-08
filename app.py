import os
from flask import Flask, url_for, render_template, request, abort, redirect, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape
import sqlite3
from sqlite3 import Error
import utils

""" 
    ** Por favor revisar la carpeta READ -LEER. Encontrará la información sobre este proyecto.
    ** Please check the folder "READ - LEER". You will find information about this project. 
"""

app = Flask(__name__)
app.secret_key = os.urandom( 24 ) #creación de secret key para firmar

#Variable global para validar funciones en las vistas html

@app.before_request
def before_request():
    usuario = session.get('usuario')
    if usuario == None:
        g.usuario = None
    else:
        g.usuario = session.get('usuario')

#Página de inicio

@app.route( '/' )
def index():
    return render_template( 'index.html' )

#Inicio de sesión con validaciones para los diferentes usuarios

@app.route('/', methods=['POST'])
def log_in():
    if request.method == 'POST':        
        email = escape(request.form['user'])
        password = escape(request.form['pass'])
        joker = ""

        try:
            with sqlite3.connect('db.db') as con:  #conectando base de datos          
                cur = con.cursor() # cursor para modificar base de dato
                result = cur.execute('SELECT * FROM users WHERE email = ? ', [email]).fetchone() #consulta
                if result == None:
                    joker = 'Usuario o contraseña inválidos, vuelve a intentarlo'
                    return render_template( 'joker.html', joker=joker), {"Refresh":"2;/"}
                hpassword = result[2]
                if (check_password_hash(hpassword,password)): #verificación de password
                    session['usuario'] = result[1] #creación de sesiones
                    session['id'] = result[0] #creación de sesiones
                    if session.get('usuario') == "Superadmin1@superadmin1.com": #creación de sesion especial
                        return redirect(url_for('homesa', a=0))
                    if session.get('usuario') == "Admin1@admin1.com": #creación de sesion especial
                        return redirect(url_for('homea',a=0))
                    return redirect(url_for('home'))
                else:
                    joker = 'Usuario o contraseña inválidos, vuelve a intentarlo' # variable para mostras en página de información y transicion. 
                    return render_template( 'joker.html', joker=joker), {"Refresh":"2;/"}     
        except Error:
            print("Ocurrió un error", Error)
            return render_template('index.html')
    else:
        return render_template('index.html')

#Vista de registro

@app.route('/registro/')
def registro():
    return render_template("registration.html")

#Función para registrarse

@app.route('/registro/', methods=["POST"])
def sign_up():
    email = escape(request.form['user']) #recuperación de datos de los form del html
    password = escape(request.form['pass'])
    joker = ""

    if not utils.isEmailValid( email ): #comprobando validez de email desde backend
        joker = "email invalido, retrocede para volverlo a intentar"
        return render_template( 'joker.html', joker=joker )                

    if not utils.isPasswordValid( password ): #comprobando validez de password desde backend
        joker = "password invalido, retrocede para volverlo a intentar"
        return render_template( 'joker.html', joker=joker )    
        
    hpassword = generate_password_hash(password) #cifrando password

    if request.method == 'POST':   
        try:
            with sqlite3.connect('db.db') as con:
                cur = con.cursor()                   
                if cur.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone() is not None: #consulta para saber si el dato ya existe en la db
                    joker = "Email ya registrado, por favor inicia sesión"
                    return render_template( 'joker.html', joker=joker ), {"Refresh": "3;/"}   
                else:
                    cur.execute( 'INSERT INTO users (email, password) VALUES (?,?) ', (email, hpassword) ) #insertar usuaro si no existe
                    con.commit()
                    joker = "Ya te encuentras registrado, por favor inicia sesión"
                    return render_template( 'joker.html', joker=joker ), {"Refresh": "3;/"}  
        except Error:
            print(Error)
            return render_template( 'registration.html' )
    else:
        return render_template( 'registration.html' )

#Página de inicio de usuario final

@app.route('/home/', methods=["GET","POST"])
def home():
    try:
        with sqlite3.connect('db.db') as con: #consulta para mostrar datos de feedback en la vista de home
            cur = con.cursor()       
            row = cur.execute('SELECT * FROM rooms').fetchall()
            rowN = len(row)
            listFeed = []
            listProm =[]
            for i in range(rowN):
                listFeed.append(cur.execute('SELECT stars FROM feedback WHERE room = ?', (i+1,)).fetchall())
            for i in range(len(listFeed)):
                for j in range(len(listFeed[i])):
                    listFeed[i][j] = listFeed[i][j][0]
            for i in range(len(listFeed)):
                if len(listFeed[i]) != 0:
                    listProm.append(round(sum(listFeed[i])/len(listFeed[i]),1))
                else:
                    listFeed[i] = 0
                    listProm.append(listFeed[i])
            return render_template("homeu.html",rowN=rowN,listProm=listProm,row=row)
    except Error:
        print("Ocurrio un error: ", Error)
        return render_template("error.html")   

#Vista de inicio SúperAdmin     

@app.route('/homesa/<int:a>')
def homesa(a):
    if a == 0:
        return render_template("homesa.html")

#Vista de inicio Admin   

@app.route('/homea/<int:a>/')
def homea(a):
    if a == 0:
        return render_template("homea.html")

#Vista de control de usuarios

@app.route('/controlu/<int:a>/<int:b>/', methods=['GET','POST'])
def controlu(a, b=0):
    if a == 0:
        try:
            with sqlite3.connect("db.db") as con: #consulta para mostrar usuarios  en la vista de administrar usuarios
                cur = con.cursor()
                rowRaw = cur.execute("SELECT * FROM users").fetchall()
                rowN = len(rowRaw)
                return render_template("controlu.html", rowN=rowN, rowRaw=rowRaw)
        except Error:
            print("Ha ocurrido un error", Error)
            return render_template("error.html")          
    if a == 1:
        try:
            with sqlite3.connect('db.db') as con: #consulta para mostrar usuarios y ser eliminados en la vista de administrar usuarios
                cur = con.cursor()
                cur.execute('DELETE FROM users WHERE id = ?', [b])
                return redirect(url_for("controlu",a=0,b=0))
        except Error:
            print("Ha ocurrido un error", Error)
            return render_template("error.html") 
        
#Vista de control de habitaciones

@app.route('/controlh/<int:a>/')
@app.route('/controlh/<int:a>/<int:b>/', methods=['GET','POST'])
def controlh(a, b=0):
    if a == 0:
        try:
            with sqlite3.connect("db.db") as con:
                cur = con.cursor()
                rowRaw = cur.execute("SELECT * FROM rooms").fetchall() #consulta para mostrar habitaciones  en la vista de administrar habitaciones
                rowN = len(rowRaw)
                return render_template("controlh.html", rowN=rowN, rowRaw=rowRaw)
        except Error:
            print("Ha ocurrido un error", Error)
            return render_template("error.html")          
    if a == 1:
        try:
            with sqlite3.connect('db.db') as con: #consulta para mostrar eliminar habitaciones en la vista de administrar habitaciones
                cur = con.cursor()
                cur.execute('DELETE FROM rooms WHERE id = ?', [b]) 
                return redirect(url_for("controlh",a=0))
        except Error:
            print("Ha ocurrido un error", Error)
            return render_template("error.html") 
    if a == 2:
        try:
            with sqlite3.connect('db.db') as con: #consulta para mostrar agregar habitaciones en la vista de administrar habitaciones
                cur = con.cursor()
                cur.execute('INSERT INTO rooms (guest, reserved) VALUES (?, ?)', [None, None])
                return redirect(url_for("controlh",a=0))
        except Error:
            print("Ha ocurrido un error", Error)
            return render_template("error.html")

#Administración de feedback 

@app.route('/feedback/<int:i>', methods=['GET','POST'])
def feed_back(i,s=0,c=0):
    c = request.form.get('comentario')
    s = request.form.get('estrellas')
    if s == None :
        return render_template('feedback.html',i=i)
    else:
        email = session.get('usuario')
        try:
            with sqlite3.connect('db.db') as con: #consulta para realizar feedback de habitaciones
                cur = con.cursor()
                r = cur.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
                rr = r[0]
                cur.execute("INSERT INTO feedback (guest, room, stars, coment) VALUES (?,?,?,?)", (rr, i, s, c))
                con.commit()
                joker = "Feedback realizado con éxito"
                return render_template( 'joker.html', joker=joker ), {"Refresh": "3;/home/"}  
            
        except Error:
            print("Ha ocurrido un error", Error)
    return redirect("error.html")

#Vista administración de comentarios 

@app.route('/editcom/<int:i>/<int:c>/', methods=["GET","POST"])
def editcom(i,c):
    if c == 0:
        try:
            with sqlite3.connect("db.db") as con: #consulta para mostrar datos de comentarios de habitaciones en la vista de administrar comentarios
                cur = con.cursor()
                row = cur.execute("SELECT * FROM feedback where guest = ?", [session.get("id")]).fetchall()
                rowN = len(row)
                return render_template("editcom.html", i=i, c=c, rowN=rowN, row=row)
        except Error:
            print("Ha ocurrido un error", Error)
            return render_template("error.html")
    if c == 1:
        idC = request.form.get("id")
        coment = request.form['coment']
        try:
            with sqlite3.connect("db.db") as con: #consulta para actualizar comentarios
                cur = con.cursor()
                row = cur.execute("SELECT * FROM feedback where guest = ?", [session.get("id")]).fetchall()
                rowN = len(row)
                
                with sqlite3.connect("db.db") as con:
                    cur = con.cursor()
                    cur.execute("UPDATE feedback SET coment = ? WHERE id = ? ", [coment, idC,])
                    con.commit()
                    print("Se actualizó con éxito")  
                    return redirect(url_for('editcom', i=i, c=0))            
        except Error:
            print("Ha ocurrido un error", Error)
            return render_template("error.html")
    if c == 1000:
        idR = request.form.get("id")
        days = request.form['reserva']
        try: 
            with sqlite3.connect("db.db") as con: #consulta para reservar habitaciones
                cur = con.cursor()
                cur.execute("UPDATE rooms SET guest = ?, reserved = ? WHERE id = ? ", [session.get("id"), days, idR])
                con.commit()
                joker = "Felicitaciones, ¡has reservado con éxito!"
                return render_template( 'joker.html', joker=joker ), {"Refresh": "3;/home/"}              
        except Error:
            print("Ha ocurrido un error", Error)
            return render_template("error.html")
    else:
        idR = request.form.get("id")
        try:
            with sqlite3.connect("db.db") as con: #consulta para elinar feedback
                cur = con.cursor()
                row = cur.execute("SELECT * FROM feedback where guest = ?", [session.get("id")]).fetchall()
                rowN = len(row)
                
                with sqlite3.connect("db.db") as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM feedback WHERE id = ?", [idR])
                    con.commit()
                    return redirect(url_for('editcom', i=i, c=0))            
        except Error:
            print("Ha ocurrido un error", Error)
            return render_template("error.html")

#Acción cerrar sesión

@app.route('/log_out/')
def log_out():
    session.pop('usuario', None)
    joker = "Cerraste sesión"
    return render_template( 'joker.html', joker=joker ), {"Refresh": "1;/"} 

#Manejo de errores

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error="pagina no encontrada"), 404

if __name__ == '__main__':
    app.run(debug=True, port=8000)