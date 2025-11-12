from flask import Flask, render_template, request

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/greet',methods=['POST'])

def greet():
    name = request.form['name']
    return f"Hello. {name}!"

if __name__ == '__main__':
    app.run(debug=True)
