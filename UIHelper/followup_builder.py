from datetime import date

markdown_format_name = "<h1><center>{}</center></h1>"
markdown_format_date = "<h3>Date: {}</h3>"
markdown_format_key_words = "<h2>Key words: {}</h2>"
markdown_format_summary = "<h2>Summary: {}</h2>"
markdown_tasks = "<h2>Tasks: </h2>"
markdown_reminders = "<h2>Reminders: </h2>"
markdown_been_done = "<h2>Been done: </h2>"
markdown_todo = "<h2>Plans: </h2>"
html_begining = "<!DOCTYPE html><html><head><style>p.dotted {{border-style: dotted;}}</style></head><body style=\"background-color: #edf0f4 !important;\"> {}"
html_ending = "</body></html>"


# Make markdown from meeting
def meeting_to_markdown(meeting_json):

    date_start = meeting_json.get('date_start') if meeting_json.get(
        'date_start') else date.today().strftime('%d.%m.%Y')
    name = meeting_json.get('name') if meeting_json.get(
        'name') else f'Meeting from {date_start}'

    key_words = ', '.join(meeting_json.get('topic'))
    summary = meeting_json.get('summary')
    #tasks = process_tasks(meeting_json)
    tasks = ', '.join(meeting_json.get('task')) if meeting_json.get('task') else 'No tasks'
    #reminders = process_reminders_and_tasks(meeting_json, 'reminder')
    reminders = ', '.join(meeting_json.get('reminder')) if meeting_json.get('reminder') else 'No reminders'
    been_done = process_colored_text(meeting_json, 'BEEN DONE')
    todo = process_colored_text(meeting_json, 'TODO')

    body = markdown_format_name.format(name) + \
        markdown_format_date.format(date_start) + \
        (markdown_format_key_words.format(key_words) if key_words else '') + \
        markdown_format_summary.format(summary) + '<hr>' + \
        (markdown_tasks + tasks + '<hr>' if tasks else '') + \
        (markdown_reminders + reminders + '<hr>' if reminders else '') + \
        (markdown_been_done + been_done + '<hr>' if been_done else '') + \
        (markdown_todo + todo + '<hr>' if todo else '')

    transcript_markdown = transcript_to_markdown(meeting_json)
    return html_begining.format(body + transcript_markdown) + html_ending


# Process meeting nodes such a 'been done' or 'todo'
def process_colored_text(meeting_json, node_name):
    nodes = meeting_json.get('colored').get(node_name)
    if not nodes:
        return ''

    text = ''
    for node in nodes:
        node_text = ''
        k = 0
        for phrase in node:
            if k % 2 == 1:
                node_text += f'<strong style="color:#0084b0;font-size:20px;">{phrase}</strong>'
            else:
                node_text += phrase

            node_text += ' '
            k += 1
        text += f'<p>{node_text}</p>'
    return text


def process_reminders_and_tasks(meeting_json, key):
    nodes = meeting_json.get(key)
    if not nodes:
        return ''

    text = ''
    for node in nodes:
        node_text = ''
        k = 0
        for phrase in node:
            if k % 2 == 1:
                node_text += f'<strong style="color:#0084b0;font-size:20px;">{phrase}</strong>'
            else:
                node_text += phrase

            node_text += ' '
            k += 1
        text += f'<p>{node_text}</p>'
    return text    


# Process tasks
def process_tasks(meeting_json):
    result_text = ''
    speakers = meeting_json.get('task')
    if not speakers:
        return ''

    for key, value in speakers.items():
        if len(value) == 0:
            continue
        speaker_text = f'<h3>Tasks from {key}: </h3>'
        for phrase in value:
            speaker_text += f'<p style="font-size:19px;"> • {phrase}</p>' if phrase else ''
        result_text += speaker_text
    return result_text


def transcript_to_markdown(meeting_json):
    format_str = "<p>{} <strong>{}:</strong> {}</p>"
    transcript = meeting_json['message_list']
    result = ''
    for message in transcript:
        result += format_str.format(message['start_time'],
                                    message['speaker'], message['text'])
    return '<h2> Transcript: </h2>' + result
