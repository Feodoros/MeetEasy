from datetime import date

task_kw_dict = ('задача', 'задание')
reminder_kw_dict = ('напоминаю', 'запомните')

markdown_format_name = "<h1><center>{}</center></h1>"
markdown_format_date = "<h2>From: {}</h2>"
markdown_format_tags = "<h2>Tags: {}</h2>"
markdown_format_summary = "<h2>Summary: {}</h2>"
markdown_format_actions = "<h2>Actions:</h2>"
markdown_format_tasks = "<p><strong>Tasks:</strong> <em>{}</em></p>"
markdown_format_reminders = "<p><strong>Reminders:</strong> <em>{}</em></p>"


def set_labels(meeting_json):
    for message in meeting_json['message_list']:
        if message['text'].lower().startswith(task_kw_dict):
            message['label'] = 'task'
        elif message['text'].lower().startswith(reminder_kw_dict):
            message['label'] = 'reminder'
        else:
            message['label'] = ''
    return meeting_json


# Make markdown from meeting
def meeting_to_markdown(meeting_json):
    def get_actions(pattern):
        return ',\n'.join(list(map(lambda x: x.get('text'),
                                   list(
                                       filter(lambda x: x.get('label') == pattern, meeting_json.get('message_list'))))))

    # Set labels as Task or Reminder for messages
    set_labels(meeting_json)

    date_start = meeting_json.get('date_start') if meeting_json.get(
        'date_start') else date.today().strftime('%d.%m.%Y')
    name = meeting_json.get('name') if meeting_json.get(
        'name') else f'Meeting from {date_start}'
    tasks = get_actions('task')
    reminders = get_actions('reminder')
    tags = meeting_json.get('tags')
    summary = meeting_json.get('summary')

    meeting_markdown = markdown_format_name.format(name) + \
        markdown_format_date.format(date_start) + \
        (markdown_format_tags.format(tags) if tags else '') + \
        markdown_format_summary.format(summary) + \
        (markdown_format_actions if tasks or reminders else '') + \
        (markdown_format_tasks.format(tasks) if tasks else '') + \
        (markdown_format_reminders.format(
            reminders) if reminders else '')

    transcript_markdown = transcript_to_markdown(meeting_json)
    return meeting_markdown + transcript_markdown


def transcript_to_markdown(meeting_json):
    format_str = "<p>{} <strong>{}:</strong> {}</p>"
    labeled_format_str = "<p>{} <strong>{}:</strong> {} (<strong>{}</strong>)</p>"
    transcript = meeting_json['message_list']
    result = ''
    for message in transcript:
        s = format_str if message['label'] == '' else labeled_format_str
        result += s.format(message['start_time'],
                           message['id'], message['text'], message['label'])
    return '<h2> Transcript: </h2>' + result
