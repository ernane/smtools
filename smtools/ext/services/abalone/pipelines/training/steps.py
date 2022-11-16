import os

import sagemaker
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.workflow.pipeline_context import PipelineSession
from sagemaker.workflow.steps import ProcessingStep

from smtools.ext.services.abalone.pipelines.training.parameters import input_data
from smtools.ext.settings.config import settings

session = PipelineSession(default_bucket=settings.default_bucket)
role_arn = sagemaker.get_execution_role()
steps = settings.services.abalone.pipelines.training.steps
training_dir = os.path.dirname(os.path.realpath(__file__))

sklearn_processor = SKLearnProcessor(
    framework_version=steps.sklearn_processor.framework_version,
    instance_type=steps.sklearn_processor.instance_type,
    instance_count=steps.sklearn_processor.instance_count,
    base_job_name="sklearn-abalone-process",
    role=role_arn,
    sagemaker_session=session,
)


processor_args = sklearn_processor.run(
    inputs=[
        ProcessingInput(
            input_name="raw", source=input_data, destination="/opt/ml/processing/input"
        ),
    ],
    outputs=[
        ProcessingOutput(output_name="train", source="/opt/ml/processing/train"),
        ProcessingOutput(output_name="validation", source="/opt/ml/processing/validation"),
        ProcessingOutput(output_name="test", source="/opt/ml/processing/test"),
    ],
    code=os.path.join(training_dir, "code", "preprocessing.py"),
)

step_process = ProcessingStep(name="AbaloneProcess", step_args=processor_args)


def init_app(app):
    # print(base_dir)
    app.steps.append(step_process)
