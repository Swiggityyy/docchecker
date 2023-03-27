from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/eprompt', methods=['POST', 'GET'])
def eprompt():
    if request.method == "POST":
        eprompt = request.form.get("eprompt")
        return "Your prompt is " + eprompt
    return render_template('index.html')

if __name__ == '__main__':
   app.run(debug = True)