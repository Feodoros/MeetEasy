from Transcriber import assembly_recognition
from UIHelper import followup_builder
from Decomposer import decomposition
from flask import Flask, render_template, render_template_string, request, send_from_directory
from turbo_flask import Turbo
import os
import json

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
        global current_file_name
        current_file_name = f.filename
        #secure_file_name = secure_filename(file_name)
        file_path = os.path.join(CACHE, current_file_name)
        f.save(file_path)

        # Transcribing meeting and voice segmentation
        update_loader('Transcribing...')
        meeting_json = assembly_recognition.transcribe_meeting(file_path)
        os.remove(file_path)

        # Decompose meeting:
        # Summary, Tasks, Reminders, plans, etc
        update_loader('Decomposing...')
        meeting_json = decomposition.decompose(meeting_json)

        with open(os.path.join(DB, f'{current_file_name}.json'), 'w+', encoding='utf-8') as f:
            json.dump(meeting_json, f, ensure_ascii=False)

        # JSON meeting to html
        meeting_html = followup_builder.meeting_to_markdown(meeting_json)
        result_path = os.path.join(
            app.template_folder, f'{current_file_name}.html')
        with open(result_path, 'w+', encoding="utf-8") as content:
            content.write(meeting_html)

        done_processing()
        return ''


@app.route('/preview', methods=['GET', 'POST'])
def display():
    return render_template(f'{current_file_name}.html')


@app.route('/download', methods=['GET', 'POST'])
def download():
    return send_from_directory(directory=app.template_folder, path=f'{current_file_name}.html')


def update_loader(message):
    template = f'<div id="loader"><center><img src="static/images/loading.gif" alt="" title="" width="200" height="200"></center><h3 class="mb-5" style="font-size: 28px;color: #0084b0;text-align:center; margin-top: 10px;">{message}</h3></div>'
    turbo.push(turbo.replace(render_template_string(template), 'loader'))


def done_processing():
    turbo.push(turbo.replace(render_template_string(
        """
    <div id="loader">
        <center>
            <h3 class="" style="font-size: 28px;color: #0084b0;text-align:center;">
                Done!
            </h3>
            <img src="static/images/check.png" alt="" title="" width="200" height="200"
                style="background-color:#edf0f4;">
            <div class="w3-show-inline-block" style="align-content: center; margin-top: 10px;">
                <div class="w3-bar">
                    <form style="float: left; margin-left: 110px;" action="/preview" target="_blank">
                        <button type="submit" class="btn btn-primary w-10">Preview</button>
                    </form>
                    <form style="float: right; margin-right: 110px;" action="/download" target="_blank">
                        <button type="submit" class="btn btn-primary w-10">Download</button>
                    </form>
                </div>
            </div>
        </center>
    </div>"""), 'loader'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
