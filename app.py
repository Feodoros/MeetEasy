from Transcriber import transcriber
from UIHelper import followup_builder
from Decomposer import decomposition
from flask import Flask, render_template, render_template_string, request, redirect, url_for
from turbo_flask import Turbo
from werkzeug.utils import secure_filename
import os
import json
import time

CURRENT_DIR = os.path.dirname(__file__)
DB = os.path.join(CURRENT_DIR, 'DB')
CACHE = os.path.join(CURRENT_DIR, '.cache')

app = Flask(__name__, template_folder=os.path.join(
    CURRENT_DIR, 'templates'), static_folder=os.path.join(CURRENT_DIR, 'static'))

turbo = Turbo(app)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        update_loader('Saving file...')
        f = request.files['files']
        file_name = f.filename
        #secure_file_name = secure_filename(file_name)
        file_path = os.path.join(CACHE, file_name)
        f.save(file_path)

        # Transcribing meeting and voice segmentation
        update_loader('Transcribing...')
        meeting_json = transcriber.transcribe_meeting(file_path)
        os.remove(file_path)

        # Decompose meeting:
        # Summary, Tasks, Reminders, plans, etc
        update_loader('Decomposing...')
        meeting_json = decomposition.decompose(meeting_json)

        with open(os.path.join(DB, f'{file_name}.json'), 'w+', encoding='utf-8') as f:
            json.dump(meeting_json, f, ensure_ascii=False)

        # JSON meeting to html
        meeting_html = followup_builder.meeting_to_markdown(meeting_json)
        result_path = os.path.join(app.template_folder, 'content.html')
        with open(result_path, 'w+', encoding="utf-8") as content:
            content.write(meeting_html)

        done_processing()
        time.sleep(3)
        return redirect(url_for("display"))


@app.route('/display')
def display():
    return render_template('content.html')


def update_loader(message):
    template = f'<div id="loader"><center><img src="static/images/loading.gif" alt="" title="" width="200" height="200"></center><h3 class="mb-5" style="font-size: 28px;color: #0084b0;text-align:center; margin-top: 10px;">{message}</h3></div>'
    turbo.push(turbo.replace(render_template_string(template), 'loader'))


def done_processing():
    turbo.push(turbo.replace(render_template_string(
        '<div id="loader"><center><img src="static/images/check.png" alt="" title="" width="200" height="200" style="background-color:#edf0f4;"></center><h3 class="mb-5" style="font-size: 28px;color: #0084b0;text-align:center; margin-top: 10px;">Done!</h3></div>'), 'loader'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
