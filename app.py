
from flask import Flask, request, render_template
from Format import start, save, to_video, clear
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/url', methods=['POST'])
def url():
    start(request.form.get("url"))
    return index()

@app.route('/download', methods=['POST'])
def download():
    save(request.json)
    return ''

@app.route('/savesettings', methods=['POST'])
def savesettings():
    data = {
        'frontend': {
            'top': request.form['top'],
            'bottom': request.form['bottom'],
            'left': request.form['left'],
            'right': request.form['right'],
            'color': request.form['color'],
            'grid': request.form['grid']
        },
        'backend': {
            #'framerate': request.form['framerate'],
            'L2': request.form['L2']
        }
    }
    with open('static/settings.json', 'w') as f:
        json.dump(data, f, indent=4)
    return index()

@app.route('/finish')
def finish():
    to_video()
    return ''

if __name__ == '__main__':
    clear()
    app.run(debug=False, host='0.0.0.0')