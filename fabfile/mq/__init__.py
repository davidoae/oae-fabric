from fabric.api import task
from fabric.operations import sudo


@task
def start():
    """Start the RabbitMQ service."""
    sudo("service rabbitmq start")


@task
def stop():
    """Stop the RabbitMQ service."""
    sudo("service rabbitmq stop")


@task
def delete_data():
    """Delete the RabbitMQ queues and their messages."""
    sudo("rabbitmqctl stop_app")
    sudo("rabbitmqctl reset")
    sudo("rabbitmqctl start_app")
