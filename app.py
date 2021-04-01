
from flask import Flask
from flask import render_template,request,redirect,url_for, flash
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key="valid"

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'Sistema'
mysql.init_app(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
   return send_from_directory(app.config['CARPETA'], nombreFoto)

@app.route('/')
def index():

    sql = "SELECT * FROM  `empleados`;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    empleados = cursor.fetchall()
    #print(empleados)
    conn.commit()

    return render_template('empleados/index.html', empleados=empleados)

@app.route('/add')
def Add():
        
    return render_template('empleados/Add.html')
    
@app.route('/edit/<int:id>')
def Edit(id):
    
    if id !='':
        #sql = "SELECT * FROM  `empleados` WHERE EmpleadoId=%s;",(id)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM  empleados WHERE EmpleadoId=%s",(id))
        empleado = cursor.fetchall()
        print(empleado)
        conn.commit()
        return render_template('empleados/Edit.html',empleado=empleado)
    
    return redirect('/')
    
@app.route('/store', methods=['POST'])
def store():
    
    _empleadoId = request.form['EmpleadoId']
    _nombre = request.form['Nombres']
    _correo = request.form['Correo']
    _foto = request.files['Foto']

    if _nombre == '' or _correo == '' or _foto == '':
        flash('You must to complete all info')
        return redirect(url_for('Add'))

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _empleadoId == '':

        nuevoNombreFoto = ''
        
        if _foto.filename !='':
            nuevoNombreFoto = tiempo + _foto.filename
            _foto.save("uploads/"+nuevoNombreFoto)

        sql = "INSERT INTO `empleados` (`EmpleadoId`, `Nombres`, `Correo`, `Foto`) VALUES (NULL, %s, %s, %s);"
        datos = (_nombre, _correo, nuevoNombreFoto)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, datos)    
        conn.commit()

        return redirect('/')
    else :
        
        sql = "UPDATE empleados SET Nombres = %s, Correo = %s WHERE EmpleadoId = %s;"
        datos = (_nombre, _correo, _empleadoId)
        conn = mysql.connect()
        cursor = conn.cursor()

        if _foto.filename !='':
            nuevoNombreFoto = tiempo + _foto.filename
            _foto.save("uploads/"+nuevoNombreFoto)
            
            cursor.execute('SELECT Foto FROM empleados WHERE EmpleadoId = %s', _empleadoId)
            fila = cursor.fetchall()
            print(fila)
            os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
            cursor.execute('UPDATE empleados SET Foto = %s WHERE EmpleadoId = %s',(nuevoNombreFoto,_empleadoId))
            conn.commit()


        cursor.execute(sql, datos)    
        conn.commit()

        return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
     if id !='':
        #sql = "SELECT * FROM  `empleados` WHERE EmpleadoId=%s;",(id)
        conn = mysql.connect()
        cursor = conn.cursor()
        
        cursor.execute('SELECT Foto FROM empleados WHERE EmpleadoId = %s', id)
        fila = cursor.fetchall()
        print(fila)
        if fila != "(('',),)":
            os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        
        cursor.execute("DELETE FROM  empleados WHERE EmpleadoId=%s",(id))
        empleado = cursor.fetchall()
        #print(empleado)
        conn.commit()
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)