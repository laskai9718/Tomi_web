from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # Ez a sor keresi meg az index.html-t a templates mappában
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)