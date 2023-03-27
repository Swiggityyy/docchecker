from flask import Flask, render_template, request
import openai
import keys
import os

openai.organization = keys.organizationid
openai.api_key = keys.apikey
openai.Model.list()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'docchecker.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def home():
        return render_template('index.html')

    @app.route('/result', methods=['POST', 'GET'])
    def eprompt():
        output = ""
        if request.method == "POST":
            eprompt = request.form.get("eprompt")
            if eprompt == "":
                eprompt = "Write a short sentence shaming me for leaving my input field blank."
            completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": eprompt}
            ]
            )
            output = completion.choices[0].message.content
        return render_template('result.html', output=output)

    from docchecker import db   
    db.init_app(app)

    from docchecker import auth
    app.register_blueprint(auth.bp)

    from docchecker import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app

