import os
import json
from Transcriber import assembly_recognition
from Transcriber import transcriber
from UIHelper import followup_builder
from Decomposer import decomposition

DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(DIR, 'Transcriber', 'data')

input_path = os.path.join(
    DATA_DIR, 'English_4.wav')
output_path = os.path.join(DATA_DIR, f'{os.path.basename(input_path)}.json')


if __name__ == '__main__':
    assembly = True
    meeting_json = {}

    if assembly:
        # AssemblyAI
        meeting_json = assembly_recognition.transcribe_meeting(input_path)
    else:
        # Yandex Speech-kit
        transcript_json = transcriber.transcribe_meeting(input_path)

    print('Meeting decomposition...')
    meeting_json = decomposition.decompose(meeting_json)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(meeting_json, f, ensure_ascii=False)

    meeting_html = followup_builder.meeting_to_markdown(meeting_json)
    result_path = os.path.join(
        DATA_DIR, f'{os.path.basename(input_path)}.html')
    with open(result_path, 'w+', encoding="utf-8") as content:
        content.write(meeting_html)

    print('All tasks done.')
