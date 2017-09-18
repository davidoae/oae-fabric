from fabric.api import task
from fabric.operations import run


@task
def start():
    """Start the RabbitMQ service."""
    run("service rabbitmq start")


@task
def stop():
    """Stop the RabbitMQ service."""
    run("service rabbitmq stop")


@task
def delete_data():
    """Delete the RabbitMQ queues and their messages."""
    run("rabbitmqctl stop_app")
    run("rabbitmqctl reset")
    run("rabbitmqctl start_app")
