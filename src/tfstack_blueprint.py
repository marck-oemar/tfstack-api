import subprocess
from flask import current_app, render_template, Blueprint, jsonify, request

from tfstack_tasks import create_tf_stack_task, delete_tf_stack_task, read_tf_stack_task
from utils import get_logger


tfstack_blueprint = Blueprint('ec2instance_blueprint', __name__)


@tfstack_blueprint.route('/', methods=['GET'])
def home():
    """Flask blueprint for /

    Returns:
        str: Simple HTML message
    """
    return "<h1>Nothing to see here</h1><p>Nothing to see here</p>"


@tfstack_blueprint.route('/tfstacks', methods=['POST'])
def create_tf_stack():
    """Flask blueprint.
       This is the Create operation, which results in a terraform apply
       of a new terraform stack, using a unique terraform state.
       The uniqueness is determined by the Terraform shell scripts that
       uses a randomly generated 'resource_id'

       Creates the related async Celery task.

    Returns:
        json: json datastructure
    """
    tf_dir = current_app.config['TF_DIR']
    celery_task = create_tf_stack_task.delay(tf_dir=tf_dir)
    return jsonify({"request_id": celery_task.id}), 202


@tfstack_blueprint.route('/tfstacks/<resource_id>', methods=['GET'])
def read_tf_stack(resource_id):
    """Flask blueprint.
       This is the Read operation, which results in a terraform state list
       of an existing terraform stack/state.

       Creates the related async Celery task.

    Returns:
        json: json datastructure
    """
    tf_dir = current_app.config['TF_DIR']
    celery_task = read_tf_stack_task.delay(
        tf_dir=tf_dir, resource_id=resource_id)
    return jsonify({"request_id": celery_task.id}), 202


@tfstack_blueprint.route('/tfstacks/<resource_id>', methods=['DELETE'])
def delete_tf_stack(resource_id):
    """Flask blueprint.
       This is the Delete operation, which results in a terraform destroy
       of an existing terraform stack/state.

       Creates the related async Celery task.

    Returns:
        json: json datastructure
    """
    tf_dir = current_app.config['TF_DIR']
    celery_task = delete_tf_stack_task.delay(
        tf_dir=tf_dir, resource_id=resource_id)
    return jsonify({"request_id": celery_task.id}), 202


@tfstack_blueprint.route("/tfstacks/requests/<request_id>", methods=["GET"])
def tfstacks_requests_AsyncResult(request_id):
    """Flask blueprint.
       Retrieves the status of a created async Celery task.

    Returns:
        json: json datastructure of the result
    """
    request_result = create_tf_stack_task.AsyncResult(request_id)

    result = {
        "request_id": request_id,
        "request_status": request_result.status,
        #  very important to convert to str, in case it's the exception
        "request_result": str(request_result.result)
    }
    return jsonify(result), 200
