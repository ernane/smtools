from sagemaker.workflow.parameters import ParameterFloat, ParameterInteger, ParameterString

from smtools.ext.settings.config import settings

# load from yaml
parameters = settings.services.abalone.pipelines.training.parameters

processing_instance_count = ParameterInteger(
    name="ProcessingInstanceCount", default_value=parameters.processing_instance_count
)
instance_type = ParameterString(
    name="TrainingInstanceType", default_value=parameters.train_instance_type
)
model_approval_status = ParameterString(
    name="ModelApprovalStatus", default_value=parameters.model_approval_status
)
input_data = ParameterString(name="InputData", default_value=parameters.input_data_uri)
batch_data = ParameterString(name="BatchData", default_value=parameters.batch_data_uri)
mse_threshold = ParameterFloat(name="MseThreshold", default_value=parameters.mse_threshold)


def init_app(app) -> None:
    app.parameters = [
        processing_instance_count,
        instance_type,
        model_approval_status,
        input_data,
        batch_data,
        mse_threshold,
    ]
