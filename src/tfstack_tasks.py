import os
import time
import subprocess
import traceback
import re
from celery import Celery, Task, states, current_task
from celery.exceptions import Ignore

from tfstack_executors import create_tf_stack, delete_tf_stack, read_tf_stack

"""Celery app and tasks that are used by both the Flask app and the Celery worker(s)
"""

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL",
                                        "redis://host.docker.internal:6379")
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://host.docker.internal:6379")


@celery.task(name="create_tf_stack_task")
def create_tf_stack_task(tf_dir):
    """
    Celery task that executes a specific Terraform shell script.

    Args:
        tf_dir (str): the path to the directory containing terraform execution shell scripts

    Returns:
        dict : containing message of status of succesful terraform apply, including the new stack/resource id.
    """

    result_create_tf_stack = create_tf_stack(tf_dir)
    return result_create_tf_stack


@celery.task(name="delete_tf_stack_task")
def delete_tf_stack_task(tf_dir, resource_id):
    """
    Celery task that executes a specific Terraform shell script.

    Args:
        tf_dir (str): the path to the directory containing terraform execution shell scripts
        resource_id (str): stack/resource id

    Returns:
        dict  : containing message of status of succesful terraform operation
    """

    result_delete_tf_stack = delete_tf_stack(tf_dir, resource_id)
    return result_delete_tf_stack


@celery.task(name="read_tf_stack_task")
def read_tf_stack_task(tf_dir, resource_id):
    """
    Celery task that executes a specific Terraform shell script.
    This is the Read operation, which results in a terraform state list

    Args:
        tf_dir (str): the path to the directory containing terraform execution shell scripts
        id (str): stack/resource id    


    Returns:
        dict : containing message of status of succesful terraform operation, including result
    """
    result_read_tf_stack = read_tf_stack(tf_dir, resource_id)
    return result_read_tf_stack
