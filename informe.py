from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlite3 import connect
import os

home = os.getcwd()


def _execute(query):
    result = None
    try:
        db_path = ("db/info.db")
        connection = connect(db_path)
        cursorobj = connection.cursor()
        cursorobj.execute(query)
        result = cursorobj.fetchall()
        connection.commit()
    except Exception as e:
        print("Error al conectar con la base de datos.", e)
    finally:
        connection.close()

    return result

app = Flask(__name__,static_url_path = "", static_folder = home)

@app.route("/", methods=["GET"])
def index():
    sql = 'SELECT ip FROM ip'
    rows = _execute(sql)
    if rows:
        tempo = []
        data = []
        for row in rows:
            tempo = str(row).split("'")
            data.append(tempo[1])
    if request.method == "GET":
        if (request.args.get('var') == None):
            ip = "Paila"
            return render_template('layout.html', posts=data, das="")
        else:
            ip = request.args.get('var')
            sql2 = "SELECT ip, port, banner.data as banner, banner.cms as cms, banner.screenshot as screenshot FROM ip, banner WHERE ip.id =banner.id AND ip.ip = '"+ip+"'"
            rows2= _execute(sql2)
            if rows2:
                #tempo3 = []
                tempo3 = {}
                for row in rows2:
                    datos = str(row).split("'")
                    #['(u', 'google.com.co', ', 80, u', 'Apache4', ', u', 'Joomla 4', ', u', '480.png', ')']
                    tempo3["ip"] = datos[1]
                    tempo2 = datos[2].split(",")
                    tempo3["port"] = tempo2[1]
                    tempo3["banner"] = datos[3]
                    tempo3["cms"] = datos[5]
                    tempo3["screen"] = datos[7]
    return render_template('layout.html', posts=data, das=tempo3)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
