from fabric.api import task
from fabric.operations import sudo


@task
def start():
    sudo("service rabbitmq start")


@task
def stop():
    sudo("service rabbitmq stop")


@task
def delete_data():
    sudo("rabbitmqctl stop_app")
    sudo("rabbitmqctl reset")
    sudo("rabbitmqctl start_app")
