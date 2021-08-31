import os
import time
import subprocess
import traceback
import re
from celery import Celery, Task, states, current_task
from celery.exceptions import Ignore

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
    This is the Create operation, which results in a terraform apply
    of a new terraform stack, using a unique terraform state.
    The uniqueness is determined by the Terraform shell scripts that
    uses a randomly generated 'stack id'

    Terraform shell script characteristics:
    - to behave as an atomic operation
    - allow for concurrent process execution, via temporary working directories
    - utilize Terraform workspaces to provide a unique Terraform state 

    Args:
        tf_dir (str): the path to the directory containing terraform execution shell scripts

    Returns:
        dict : containing message of status of succesful terraform apply, including the new stack/resource id.
    """
    script_errors=['error:ExistingWorkspaceContainsResources']

    try:
        print(id)
        cmd = './create_tfstack.sh'
        process = subprocess.Popen(cmd,
                                   shell=True,
                                   executable='/bin/sh',
                                   cwd=tf_dir,
                                   stdout=subprocess.PIPE)
    except Exception:
        error_message = "Encountered an backend error. Unable to execute Terraform executor"
        raise Exception(error_message)

    # process output
    piped_output = ''
    resource_id_line = ''
    error_line = ''

    while True:
        line = process.stdout.readline()
        if not line:
            break
        line_stripped = line.decode('utf8', errors='strict').strip()
        print(line_stripped)
        piped_output += line_stripped
        # catch particular messages
        if line_stripped is not None:
            if 'resource_id' in line_stripped:
                resource_id_line = line_stripped
            for i in script_errors:
                if i in line_stripped:
                    error_line = i
                    break

    process.wait()
    # evaluate script process
    if process.returncode == 0:
        regex_result_list = re.findall('"([^"]*)"', resource_id_line)
        if len(regex_result_list) != 1:
            resource_id = 'could not determine'
        else:
            resource_id = regex_result_list[0]
        message = {
            'message': "TFstack created succesfully",
            'resource_id': resource_id
        }
        return message
    else:
        if error_line:
            message = {
                'message': error_line,
            }
        else:
            message = {
                'message': "Unknown error occured during execution of Terraform executor",
            }
        raise Exception(message)


@celery.task(name="delete_tf_stack_task")
def delete_tf_stack_task(tf_dir, id):
    """
    Celery task that executes a specific Terraform shell script.
    This is the Delete operation, which results in a terraform destroy

    Terraform shell script characteristics:
    - to behave as an atomic operation
    - allow for concurrent process execution, via temporary working directories
    - utilize Terraform workspaces to provide a unique Terraform state 

    Args:
        tf_dir (str): the path to the directory containing terraform execution shell scripts
        id (str): stack/resource id

    Returns:
        dict : containing message of status of succesful terraform operation
    """
    script_errors=['error:IdNotSpecified','error:WorkspaceNotExist']

    try:
        print(id)
        cmd = './delete_tfstack.sh' + ' ' + id

        process = subprocess.Popen(cmd,
                                   shell=True,
                                   executable='/bin/sh',
                                   cwd=tf_dir,
                                   stdout=subprocess.PIPE)
    except Exception:
        error_message = "Encountered an backend error. Unable to execute Terraform executor"
        raise Exception(error_message)

    # process output
    piped_output = ''
    error_line = ''

    while True:
        line = process.stdout.readline()
        if not line:
            break
        line_stripped = line.decode('utf8', errors='strict').strip()
        print(line_stripped)
        piped_output += line_stripped
        # catch particular messages
        if line_stripped is not None:
            for i in script_errors:
                if i in line_stripped:
                    error_line = i
                    break

    process.wait()
    # evaluate script process
    if process.returncode == 0:
        message = {
            'message': "TFstack" + " deleted succesfully",
        }
        return message
    else:
        if error_line:
            message = {
                'message': error_line,
            }
        else:
            message = {
                'message': "Unknown error occured during execution of Terraform executor",
            }
        raise Exception(message)


@celery.task(name="read_tf_stack_task")
def read_tf_stack_task(tf_dir, id):
    """
    Celery task that executes a specific Terraform shell script.
    This is the Read operation, which results in a terraform state list

    Terraform shell script characteristics:
    - to behave as an atomic operation
    - allow for concurrent process execution, via temporary working directories
    - utilize Terraform workspaces to provide a unique Terraform state 

    Args:
        tf_dir (str): the path to the directory containing terraform execution shell scripts
        id (str): stack/resource id    


    Returns:
        dict : containing message of status of succesful terraform operation, including result
    """
    script_errors=['error:IdNotSpecified','error:WorkspaceNotExist']

    try:
        print(id)
        cmd = './read_tfstack.sh' + ' ' + id

        process = subprocess.Popen(cmd,
                                   shell=True,
                                   executable='/bin/sh',
                                   cwd=tf_dir,
                                   stdout=subprocess.PIPE)
    except Exception:
        error_message = "Encountered an backend error. Unable to execute Terraform executor"
        raise Exception(error_message)

    # process output
    piped_output = ''
    error_line = ''

    while True:
        line = process.stdout.readline()
        if not line:
            break
        line_stripped = line.decode('utf8', errors='strict').strip()
        print(line_stripped)
        piped_output += line_stripped
        # catch particular messages
        if line_stripped is not None:
            for i in script_errors:
                if i in line_stripped:
                    error_line = i
                    break

    process.wait()
    # evaluate script process
    if process.returncode == 0:
        message = {
            'message': "TFstack" + " read succesfully",
            'content': piped_output
        }
        return message
    else:
        if error_line:
            message = {
                'message': error_line,
            }
        else:
            message = {
                'message': "Unknown error occured during execution of Terraform executor",
            }
        raise Exception(message)


