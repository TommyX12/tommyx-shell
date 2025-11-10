from todoist_api_python.api import TodoistAPI
import os


def get_todoist_api(token=None):
    if token is None:
        token = os.getenv("TODOIST_API_TOKEN")

    if not token:
        raise ValueError("TODOIST_API_TOKEN is not set")

    return TodoistAPI(token)


def add_task_to_project(title, project_id=None, token=None):
    api = get_todoist_api(token)
    api.add_task(content=title, project_id=project_id)


def get_tasks(project_id=None, token=None):
    api = get_todoist_api(token)
    return [
        task
        for task_list in api.get_tasks(project_id=project_id)
        for task in task_list
    ]


def delete_task(task_id, token=None):
    api = get_todoist_api(token)
    api.delete_task(task_id)


def delete_tasks(task_ids, token=None):
    api = get_todoist_api(token)

    for task_id in task_ids:
        api.delete_task(task_id)


def get_projects(token=None):
    api = get_todoist_api(token)
    return [
        project
        for project_list in api.get_projects()
        for project in project_list
    ]


def get_inbox_project_id(token=None):
    for project in get_projects(token):
        if project.is_inbox_project:
            return project.id

    return None
