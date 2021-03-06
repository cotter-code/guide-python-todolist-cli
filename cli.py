from PyInquirer import prompt
import requests
import click
import os
import cotter
from cotter import tokenhandler
token_file_name = "cotter_token.json"

# 1️⃣ Add your Cotter API KEY ID here
api_key = "YOUR API KEY ID"


@click.group()
def main():
    """ A Todo List CLI """
    pass


@main.command()
def login():
    """Login to use the API"""
    # Add a file called `cotter_login_success.html`
    # Call Cotter's api to login
    port = 8080  # Select a port
    response = cotter.login_with_email_link(api_key, port)

    # 1️⃣ Add your Cotter API KEY ID here
    url = 'https://cottertodolist.herokuapp.com/login_register'
    headers = {'Content-Type': 'application/json'}
    data = response
    resp = requests.post(url, json=data, headers=headers)

    if resp.status_code != 200:
        resp.raise_for_status()
    tokenhandler.store_token_to_file(response["oauth_token"], token_file_name)
    click.echo(resp.json())


@main.command()
@click.option('--name', prompt='List name', help='Name for your new todo list')
def create(name):
    """Create a todo list"""
    # Get access token
    access_token = tokenhandler.get_token_from_file(
        token_file_name, api_key)["access_token"]

    # Construct request
    url = "https://cottertodolist.herokuapp.com/list/create"
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + access_token}
    data = {"name": name}
    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        response.raise_for_status()

    click.echo("List " + name + " created!")


@main.command()
def add():
    """Create a todo task for a list"""
    # Get access token from file
    access_token = tokenhandler.get_token_from_file(
        token_file_name, api_key)["access_token"]

    # Get all todo lists for the user
    url = "https://cottertodolist.herokuapp.com/list"
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(url, headers=headers)
    lists = response.json()

    # Prompt to pick list
    options = map(lambda x: x["name"], lists)
    questions = [
        {
            'type': 'list',
            'name': 'list_name',
            'message': 'Add task to which list?',
            'choices': options,
        },
        {
            'type': 'input',
            'name': 'task_name',
            'message': 'Task description',
        }
    ]
    answers = prompt(questions)
    if not answers:
        return

    # Call API to create task fot the selected list
    url = "https://cottertodolist.herokuapp.com/todo/create"
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + access_token}
    data = {
        "name": answers['list_name'],
        "task": answers['task_name']
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        response.raise_for_status()

    click.echo("Task " + answers['task_name'] +
               " is added in list " + answers['list_name'])


@main.command()
@click.option('-a', '--all', is_flag=True)  # Make a boolean flag
def ls(all):
    """Show lists"""
    # Get access token from file
    access_token = tokenhandler.get_token_from_file(
        token_file_name, api_key)["access_token"]

    # Get all lists
    url = "https://cottertodolist.herokuapp.com/list"
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        response.raise_for_status()
    listsFormatted = response.json()

    if all == True:
        # Show all tasks in all lists
        for chosenList in listsFormatted:
            click.echo('\n' + chosenList['name'])
            for task in chosenList['tasks']:
                if task['done'] == True:
                    click.echo("[✔] " + task['task'])
                else:
                    click.echo("[ ] " + task['task'])
    else:
        # Show a prompt to choose a list
        questions = [
            {
                'type': 'list',
                'name': 'list',
                'message': 'Which list do you want to see?',
                'choices': list(map(lambda lst: lst['name'], listsFormatted))
            },
        ]
        answers = prompt(questions)
        if not answers:
            return

        # Get the chosen list
        chosenList = list(
            filter(lambda lst: lst['name'] == answers['list'], listsFormatted))
        if len(chosenList) <= 0:
            click.echo("Invalid choice of list")
            return
        chosenList = chosenList[0]

        # Show tasks in the chosen list
        click.echo(chosenList['name'])
        for task in chosenList['tasks']:
            if task['done'] == True:
                click.echo("[✔] " + task['task'])
            else:
                click.echo("[ ] " + task['task'])


@main.command()
def toggle():
    """Update tasks in a list"""
    # Get access token from file
    access_token = tokenhandler.get_token_from_file(
        token_file_name, api_key)["access_token"]

    # Call API to list all tasks
    url = "https://cottertodolist.herokuapp.com/list"
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        response.raise_for_status()
    listsFormatted = response.json()

    # Show a prompt to choose a list
    questions = [
        {
            'type': 'list',
            'name': 'list',
            'message': 'Which list do you want to update?',
            'choices': list(map(lambda lst: lst['name'], listsFormatted))
        },
    ]
    answers = prompt(questions)
    if not answers:
        return

        # Get the chosen list
    chosenList = list(
        filter(lambda lst: lst['name'] == answers['list'], listsFormatted))
    if len(chosenList) <= 0:
        click.echo("Invalid choice of list")
        return
    chosenList = chosenList[0]

    # Show an interactive checklist for the tasks
    questions = [
        {
            'type': 'checkbox',
            'message': chosenList['name'],
            'name': chosenList['name'],
            'choices': list(map(lambda task: {'name': task['task'], 'checked': task["done"]}, chosenList['tasks'])),
        }
    ]
    answers = prompt(questions)
    if not answers:
        return

        # Call our Update API for each task in the list
    # set `done` as True or False based on answers
    for task in chosenList['tasks']:
        url = "https://cottertodolist.herokuapp.com/todo/update/done/" + \
            task['id']
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + access_token}
        data = {
            "done": task['task'] in answers[chosenList['name']]
        }
        response = requests.put(url, json=data, headers=headers)
        if response.status_code != 200:
            response.raise_for_status()

    click.echo(answers)


if __name__ == "__main__":
    main()
