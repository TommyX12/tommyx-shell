from utils.todoist import get_tasks, get_inbox_project_id, delete_task
from utils.obsidian import add_reading_note

def add_task_to_reading_notes(task):
    # parse the url. if task.content itself is entirely a url, use that as the url. otherwise, check if task.content is a markdown link. if so, parse it into url and title.
    task_title = task.content.strip()
    if task_title.startswith('['):
        # parse markdown link
        url = task_title.split('](')[1].split(')')[0]
        title_candidate = task_title.split('](')[0].strip('[')
        if title_candidate.lower().startswith('http'):
            title = None
        else:
            title = title_candidate
    else:
        url = task_title
        title = None

    # parse tags and notes
    # tags are all labels that are not "research"
    tags = [label for label in task.labels if label != 'research']
    # notes is the task.description
    notes = (task.description or "").strip()

    add_reading_note(url, title, tags, notes)

def main():
    inbox_project_id = get_inbox_project_id()
    tasks = get_tasks(inbox_project_id)
    for task in tasks:
        if task.labels and 'research' in task.labels:
            try:
                add_task_to_reading_notes(task)
                delete_task(task.id)
            except Exception as e:
                print(f"Error adding task to reading notes: {e}")


if __name__ == '__main__':
    main()