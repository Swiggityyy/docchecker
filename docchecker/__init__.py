from flask import Flask, render_template, request
app = Flask(__name__)
import openai
import keys

openai.organization = keys.organizationid
openai.api_key = keys.apikey
openai.Model.list()

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/eprompt', methods=['POST', 'GET'])
def eprompt():
    output = ""
    if request.method == "POST":
        eprompt = request.form.get("eprompt")
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
         messages=[
        {"role": "system", "content": eprompt}
        ]
        )
        output = completion.choices[0].message.content
    return render_template('index.html', output=output)

if __name__ == '__main__':
   app.run(debug = True)