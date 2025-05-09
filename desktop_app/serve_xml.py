from flask import Flask, send_file
app = Flask(__name__)

@app.route('/procesos')
def procesos():
    return send_file('desktop_app/procesos.xml', mimetype='application/xml')

if __name__ == '__main__':
    app.run(port=5000) 