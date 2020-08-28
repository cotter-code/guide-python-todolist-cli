#!/usr/bin/env python

from PyInquirer import prompt
import requests
import click
import os
import sys
import cotter
from cotter import tokenhandler
token_file_name = os.path.join(sys.path[0], "cotter_token.json")

# 1️⃣ Add your Cotter API KEY ID here
api_key = os.getenv("TODO_LIST_API_KEY_ID")


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
@click.argument('listname', required=False)
def create(listname):
    """Create a todo list"""
    # Get access token
    access_token = tokenhandler.get_token_from_file(
        token_file_name, api_key)["access_token"]

    # Construct request
    if not listname or len(listname) <= 0 or listname == '.':
        listname = os.getcwd()
    url = "https://cottertodolist.herokuapp.com/list/create"
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + access_token}
    data = {"name": listname}
    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        response.raise_for_status()

    click.echo('List "' + listname + '" created!')


@main.command()
@click.argument('listname', required=False)
@click.argument('taskname', required=False)
def add(listname, taskname):
    """Create a todo task for a list"""
    # Get access token from file
    access_token = tokenhandler.get_token_from_file(
        token_file_name, api_key)["access_token"]

    # Get all todo lists for the user
    url = "https://cottertodolist.herokuapp.com/list"
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(url, headers=headers)
    lists = response.json()

    if not listname or len(listname) <= 0:
        # Prompt to pick list
        options = map(lambda x: x["name"], lists)
        questions = [
            {
                'type': 'list',
                'name': 'list_name',
                'message': 'Add task to which list?',
                'choices': options,
            },
        ]
        answers = prompt(questions)
        if not answers:
            return
        listname = answers['list_name']
    elif listname == '.':
        listname = os.getcwd()

    if not taskname or len(taskname) <= 0:
        # Prompt for task name
        questions = [
            {
                'type': 'input',
                'name': 'task_name',
                'message': 'Task description',
            }
        ]
        answers = prompt(questions)
        if not answers:
            return
        taskname = answers['task_name']

    # Call API to create task fot the selected list
    url = "https://cottertodolist.herokuapp.com/todo/create"
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + access_token}
    data = {
        "name": listname,
        "task": taskname
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        response.raise_for_status()

    click.echo('Task "' + taskname +
               '" is added in list "' + listname + '"')


@main.command()
@click.argument('listname', required=False)
@click.option('-a', '--all', is_flag=True)  # Make a boolean flag
def ls(listname, all):
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
        if not listname or len(listname) <= 0:
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
            listname = answers['list']
        elif listname == '.':
            listname = os.getcwd()

        # Get the chosen list
        chosenList = list(
            filter(lambda lst: lst['name'] == listname, listsFormatted))
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
@click.argument('listname', required=False)
def toggle(listname):
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

    if not listname or len(listname) <= 0:
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
        listname = answers['list_name']
    elif listname == '.':
        listname = os.getcwd()

        # Get the chosen list
    chosenList = list(
        filter(lambda lst: lst['name'] == listname, listsFormatted))
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


@main.command()
@click.argument('listname', required=False)
@click.option('-rf', '--removelist', is_flag=True)  # Make a boolean flag
def rm(removelist, listname):
    """Delete a task in a list or delete a whole list"""
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

    if not listname or len(listname) <= 0:
        # Show a prompt to choose a list
        questions = [
            {
                'type': 'list',
                'name': 'list',
                'message': 'Which list do you want to delete' if removelist else 'Which list does the task belongs to?',
                'choices': list(map(lambda lst: lst['name'], listsFormatted))
            },
        ]
        answers = prompt(questions)
        if not answers:
            return
        listname = answers['list']
    elif listname == '.':
        listname = os.getcwd()

    # Get the chosen list
    chosenList = list(
        filter(lambda lst: lst['name'] == listname, listsFormatted))
    if len(chosenList) <= 0:
        click.echo("Invalid choice of list")
        return
    chosenList = chosenList[0]

    if (removelist == True):
        # Remove the list
        url = "https://cottertodolist.herokuapp.com/list/delete/" + \
            chosenList['id']
        headers = {'Authorization': 'Bearer ' + access_token}
        response = requests.delete(url,  headers=headers)
        if response.status_code != 200:
            response.raise_for_status()
        click.echo('List "' + chosenList['name'] + '" is deleted')
        return

    # Remove a task from list
    # Option to pick a task
    questions = [
        {
            'type': 'list',
            'message': chosenList['name'],
            'name': 'task',
            'choices': list(map(lambda task: task['task'], chosenList['tasks'])),
        }
    ]
    answers = prompt(questions)
    if not answers:
        return

    # Get the chosen task
    chosenTask = list(
        filter(lambda task: task['task'] == answers['task'], chosenList['tasks']))
    if len(chosenTask) <= 0:
        click.echo("Invalid choice of task")
        return
    chosenTask = chosenTask[0]

    # Call our Delete API
    url = "https://cottertodolist.herokuapp.com/todo/delete/" + \
        chosenTask['id']
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.delete(url,  headers=headers)
    if response.status_code != 200:
        response.raise_for_status()
    click.echo('Task "' + chosenList['name'] + '" is deleted')
    return


if __name__ == "__main__":
    main()
