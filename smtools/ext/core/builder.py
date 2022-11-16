import os

from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.workflow.parameters import ParameterFloat, ParameterInteger, ParameterString
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep

from smtools import base_dir, logger
from smtools.ext.core.abstract import AbstractTraining
from smtools.ext.core.factory import sagemaker_processor_factory


class TrainingBuilder(AbstractTraining):
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._pipeline = Pipeline(name="abalone")

    @property
    def pipeline(self) -> Pipeline:
        pipeline = self._pipeline
        self.reset()
        return pipeline

    def produce_paramters(self, parameters) -> None:
        """workflow Parameters"""
        logger.info("Add parameter ProcessingInstanceCount")
        self._pipeline.parameters.append(
            ParameterInteger(
                name="ProcessingInstanceCount", default_value=parameters.processing_instance_count
            )
        )

        logger.info("Add parameter TrainingInstanceType")
        self._pipeline.parameters.append(
            ParameterString(
                name="TrainingInstanceType", default_value=parameters.train_instance_type
            )
        )

        logger.info("Add parameter ModelApprovalStatus")
        self._pipeline.parameters.append(
            ParameterString(
                name="ModelApprovalStatus", default_value=parameters.model_approval_status
            )
        )

        logger.info("Add parameter InputData")
        self._pipeline.parameters.append(
            ParameterString(name="InputData", default_value=parameters.input_data_uri)
        )

        logger.info("Add parameter BatchData")
        self._pipeline.parameters.append(
            ParameterString(name="BatchData", default_value=parameters.batch_data_uri)
        )

        logger.info("Add parameter MseThreshold")
        self._pipeline.parameters.append(
            ParameterFloat(name="MseThreshold", default_value=parameters.mse_threshold)
        )

    def produce_pre_process_data(self, config) -> None:
        """Feature Engineering"""
        processor = sagemaker_processor_factory.get_or_create(
            service=config.steps.pre_process_data.processor, **config.steps.pre_process_data
        )
        processor_args = processor.run(
            inputs=[
                ProcessingInput(
                    input_name=input.input_name, source=input.source, destination=input.destination
                )
                for input in config.steps.pre_process_data.inputs
            ],
            outputs=[
                ProcessingOutput(output_name=output.output_name, source=output.source)
                for output in config.steps.pre_process_data.outputs
            ],
            code=os.path.join(
                base_dir,
                config.steps.pre_process_data.source_dir,
                config.steps.pre_process_data.code,
            ),
        )
        step_process = ProcessingStep(
            name=config.steps.pre_process_data.name, step_args=processor_args
        )

        self._pipeline.steps.append(step_process)

    def produce_train(self) -> None:
        """Model Training"""
        pass

    def produce_evaluation(self) -> None:
        """Model Evaluation"""
        pass

    def produce_condition(self) -> None:
        """
        Model Accuracy

        if metric_threshold
            - Model Create
            - Model Package
        else
            - Execution Failed
        """
        pass
