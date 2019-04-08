from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
   return render_template(‘hello.html’)

@app.route('/hello/<user>')
def hello_name(user):
   return render_template('hello.html', name = user)

if __name__ == '__main__':
   app.run(debug = True)