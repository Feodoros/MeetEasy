from datetime import date

markdown_format_name = "<h1><center>{}</center></h1>"
markdown_format_date = "<h2>From: {}</h2>"
markdown_format_key_words = "<h2>Key words: {}</h2>"
markdown_format_summary = "<h2>Summary: {}</h2>"
markdown_format_tasks = "<p><strong>Tasks:</strong> <em>{}</em></p>"
markdown_format_reminders = "<p><strong>Reminders:</strong> <em>{}</em></p>"
markdown_format_been_done = "<p><strong>Been done:</strong> <em>{}</em></p>"
markdown_format_todo = "<p><strong>TODO:</strong> <em>{}</em></p>"


# Make markdown from meeting
def meeting_to_markdown(meeting_json):

    date_start = meeting_json.get('date_start') if meeting_json.get(
        'date_start') else date.today().strftime('%d.%m.%Y')
    name = meeting_json.get('name') if meeting_json.get(
        'name') else f'Meeting from {date_start}'

    key_words = meeting_json.get('topic')
    summary = meeting_json.get('summary')
    tasks = meeting_json.get('task')
    reminders = meeting_json.get('reminder')
    been_done = process_meeting_node(meeting_json, 'BEEN DONE')
    todo = process_meeting_node(meeting_json, 'TODO')

    meeting_markdown = markdown_format_name.format(name) + \
        markdown_format_date.format(date_start) + \
        (markdown_format_key_words.format(key_words) if key_words else '') + \
        markdown_format_summary.format(summary) + \
        (markdown_format_tasks.format(tasks) if tasks else '') + \
        (markdown_format_reminders.format(reminders) if reminders else '') + \
        (markdown_format_been_done.format(been_done) if been_done else '') + \
        (markdown_format_todo.format(todo) if todo else '')

    transcript_markdown = transcript_to_markdown(meeting_json)
    return meeting_markdown + transcript_markdown


# Process meeting nodes such a 'been done' or 'todo'
def process_meeting_node(meeting_json, node_name):
    nodes = meeting_json.get('colored').get(node_name)
    if not nodes:
        return ''

    text = ''
    k = 0
    for node in nodes:
        node_text = ''
        for phrase in node:
            if k % 2 == 1:
                node_text += f'<strong>{phrase}</strong>'
            else:
                node_text += phrase

            node_text += ' '
            k += 1
        text += f'<p>{node_text}</p>'
    return text


def transcript_to_markdown(meeting_json):
    format_str = "<p>{} <strong>{}:</strong> {}</p>"
    transcript = meeting_json['message_list']
    result = ''
    for message in transcript:
        result += format_str.format(message['start_time'],
                                    message['speaker'], message['text'])
    return '<h2> Transcript: </h2>' + result
