import followup_builder
import json
import os


DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(DIR, 'data')

test_followup = os.path.join(DATA_DIR, '0_en.json')
output_path = os.path.join(DATA_DIR, '0_en_output.html')


if __name__ == '__main__':
    with open(test_followup, encoding='utf-8') as f:
        meeting_json = json.load(f)

    content_html = followup_builder.meeting_to_markdown(meeting_json)
    with open(output_path, 'w+', encoding="utf-8") as content:
            content.write(content_html)

