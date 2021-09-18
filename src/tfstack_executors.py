import re
import subprocess
from utils import get_logger


def parse_process_output(process: subprocess.Popen):
    """
    Parses and print output from subprocess.Popen

    Args:
        process (subprocess.Popen): subprocess.Popen

    Returns:
        list: output from process
    """
    logger = get_logger()

    # process output
    piped_output = list()
    resource_id_line = ''
    error_line = ''

    while True:
        # stream
        line = process.stdout.readline()
        if not line:
            break
        line_stripped = line.decode('utf8', errors='strict').strip()
        logger.info(line_stripped)
        piped_output.append(line_stripped)

    process.wait()
    return piped_output


def grep_script_error(process_output: list, script_errors: list):
    """
    Grep a script error

    Args:
        process_output (list): 
        script_errors (list): 

    Returns:
        [type]: Returns the first found string of error or None
    """
    # loop through the output lines
    for line in process_output:
        for i in script_errors:
            if i in line:
                return i
    return None


def grep_resource_id(process_output: list, resource_id_grep_pattern: str):
    """
    Grep resource_id from terraform output

    Args:
        process_output (list): 
        resource_id_grep_pattern (str): 

    Returns:
        str: resource id
    """
    # loop through the output lines

    resource_id_line = None
    for line in process_output:
        if resource_id_grep_pattern in line:
            resource_id_line = line
            break
    if not resource_id_line:
        return None

    # specific terraform output
    regex_result_list = re.findall('"([^"]*)"', resource_id_line)
    if len(regex_result_list) != 1:
        return None
    else:
        resource_id = regex_result_list[0]
        return resource_id


def create_tf_stack(tf_dir):
    """
    Executes the terraform shell script create_tfstack.
    Handles the output and errors. 

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

    Raises:
        Exception: "Unable to execute Terraform executor"
        Exception: "Error! Executed Terraform executor succesfully, but did not get an resource_id back"
        Exception: "Unknown error occured during execution of Terraform executor"


    Returns:
        str: 'message': "TFstack created succesfully"
    """
    logger = get_logger()

    script_errors = ['error:ExistingWorkspaceContainsResources']

    try:
        cmd = './create_tfstack.sh'
        process = subprocess.Popen(cmd,
                                   shell=True,
                                   executable='/bin/sh',
                                   cwd=tf_dir,
                                   stdout=subprocess.PIPE)
    except Exception:
        error_message = "Unable to execute Terraform executor"
        raise Exception(error_message)

    # process output
    process_output = parse_process_output(process)
    logger.info(process_output)
    # evaluate script process
    if process.returncode == 0:
        resource_id = grep_resource_id(
            process_output=process_output, resource_id_grep_pattern='resource_id')
        if resource_id:
            message = {
                'message': "TFstack created succesfully",
                'resource_id': resource_id
            }
            return message
        else:
            error_message = "Error! Executed Terraform executor succesfully, but did not get an resource_id back"
            raise Exception(error_message)
    else:
        script_error = grep_script_error(process_output, script_errors)
        if script_error:
            error_message = script_error
        else:
            error_message = "Unknown error occured during execution of Terraform executor"
        raise Exception(error_message)


def delete_tf_stack(tf_dir: str, resource_id: str):
    """
    Executes the terraform shell script delete_tfstack.
    Handles the output and errors. 

    This is the Delete operation, which results in a terraform destroy

    Terraform shell script characteristics:
    - to behave as an atomic operation
    - allow for concurrent process execution, via temporary working directories
    - utilize Terraform workspaces to provide a unique Terraform state 

    Args:
        tf_dir (str): the path to the directory containing terraform execution shell scripts
        resource_id (str): stack/resource id

    Raises:
        Exception: "Unable to execute Terraform executor"
        Exception: "Unknown error occured during execution of Terraform executor",

    Returns:
        str: "TFstack" + " deleted succesfully"
    """
    logger = get_logger()

    script_errors = ['error:IdNotSpecified', 'error:WorkspaceNotExist']

    try:
        logger.info(id)
        cmd = './delete_tfstack.sh' + ' ' + resource_id

        process = subprocess.Popen(cmd,
                                   shell=True,
                                   executable='/bin/sh',
                                   cwd=tf_dir,
                                   stdout=subprocess.PIPE)
    except Exception:
        error_message = "Unable to execute Terraform executor"
        raise Exception(error_message)

    # process output
    process_output = parse_process_output(process)

    # evaluate script process
    if process.returncode == 0:
        message = {
            'message': "TFstack deleted succesfully",
        }
        return message
    else:
        script_error = grep_script_error(process_output, script_errors)
        if script_error:
            error_message = script_error
        else:
            error_message = "Unknown error occured during execution of Terraform executor"
        raise Exception(error_message)


def read_tf_stack(tf_dir: str, resource_id: str):
    """
    Executes the terraform shell script read_tfstack.
    Handles the output and errors. 

    Terraform shell script characteristics:
    - to behave as an atomic operation
    - allow for concurrent process execution, via temporary working directories
    - utilize Terraform workspaces to provide a unique Terraform state 

    Args:
        tf_dir (str): the path to the directory containing terraform execution shell scripts
        id (str): stack/resource id    

    Raises:
    Raises:
        Exception: "Unable to execute Terraform executor"
        Exception: "Unknown error occured during execution of Terraform executor",

    Returns:
        dict : containing message of status of succesful terraform operation, including result
    """
    logger = get_logger()

    script_errors = ['error:IdNotSpecified', 'error:WorkspaceNotExist']

    try:
        logger.info(id)
        cmd = './read_tfstack.sh' + ' ' + resource_id

        process = subprocess.Popen(cmd,
                                   shell=True,
                                   executable='/bin/sh',
                                   cwd=tf_dir,
                                   stdout=subprocess.PIPE)
    except Exception:
        error_message = "Unable to execute Terraform executor"
        raise Exception(error_message)

    # process output
    process_output = parse_process_output(process)

    # evaluate script process
    if process.returncode == 0:
        message = {
            'message': "TFstack read succesfully",
            'content': process_output
        }
        return message
    else:
        script_error = grep_script_error(process_output, script_errors)
        if script_error:
            error_message = script_error
        else:
            error_message = "Unknown error occured during execution of Terraform executor"
        raise Exception(error_message)
