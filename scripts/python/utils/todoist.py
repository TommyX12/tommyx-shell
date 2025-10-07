from todoist_api_python.api import TodoistAPI


def get_todoist_api(token=None):
    if token is None:
        token = os.getenv("TODOIST_API_TOKEN")

    return TodoistAPI(token)


def add_task_to_project(title, project_id=None, token=None):
    api = get_todoist_api(token)
    api.add_task(content=title, project_id=project_id)


def get_tasks(project_id=None, token=None):
    api = get_todoist_api(token)
    return api.get_tasks(project_id=project_id)


def delete_tasks(task_ids, token=None):
    api = get_todoist_api(token)

    for task_id in task_ids:
        api.delete_task(task_id)


def print_projects(token=None):
    api = get_todoist_api(token)

    projects = api.get_projects()

    print("All projects:")
    for project in projects:
        print(project)