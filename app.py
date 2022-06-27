from Transcriber import transcriber
from UIHelper import followup_builder
from Decomposer import decomposition
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import json

CURRENT_DIR = os.path.dirname(__file__)
DB = os.path.join(CURRENT_DIR, 'DB')
CACHE = os.path.join(CURRENT_DIR, '.cache')

app = Flask(__name__, template_folder=os.path.join(
    CURRENT_DIR, 'templates'), static_folder=os.path.join(CURRENT_DIR, 'static'))


@app.route('/')
def upload_file():
    return render_template('index.html')


@app.route('/display', methods=['GET', 'POST'])
def save_file():
    if request.method == 'POST':
        f = request.files['files']
        file_name = secure_filename(f.filename)
        file_path = os.path.join(CACHE, file_name)
        f.save(file_path)

        # Transcribing meeting and voice segmentation
        meeting_json = transcriber.transcribe_meeting(file_path)
        with open(os.path.join(DB, f'{f.filename}.json'), 'w+', encoding='utf-8') as f:
            json.dump(meeting_json, f, ensure_ascii=False)
        os.remove(file_path)

        # Decompose meeting:
        # Summary, Tasks, Reminders, plans, etc
        meeting_json = decomposition.decompose(meeting_json)

        # JSON meeting to html
        meeting_html = followup_builder.meeting_to_markdown(meeting_json)
        #content = meeting_html
        result_path = os.path.join(app.template_folder, 'content.html')
        with open(result_path, 'w+', encoding="utf-8") as content:
            content.write(meeting_html)

    return render_template('content.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
