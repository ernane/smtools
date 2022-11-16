from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod

import sagemaker
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.workflow.parameters import ParameterFloat, ParameterInteger, ParameterString
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import PipelineSession
from sagemaker.workflow.steps import ProcessingStep

from smtools.ext.settings.config import settings

logger = logging.getLogger()
logging.basicConfig(format="[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s")
logger.setLevel(logging.INFO)

session = PipelineSession(default_bucket=settings.default_bucket)
role_arn = sagemaker.get_execution_role()

# /home/ejjunior/Workspace/templates/cookiecutter-sagemaker/smtools
base_dir = os.path.dirname(os.path.realpath(__file__))


class ObjectFactory:
    def __init__(self):
        self._builders = {}

    @property
    def builders(self):
        return self._builders

    def register_builder(self, key, builder):
        self._builders[key] = builder

    def create(self, key, **kwargs):
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)


class SKLearnProcessorBuilder:
    def __init__(self) -> None:
        self._instance = None

    def __call__(
        self, framework_version, instance_type, instance_count, base_job_name, **_ignored
    ) -> SKLearnProcessor:
        if not self._instance:
            self._instance = SKLearnProcessor(
                framework_version=framework_version,
                instance_type=instance_type,
                instance_count=instance_count,
                base_job_name=base_job_name,
                role=role_arn,
                sagemaker_session=session,
            )
        return self._instance


class AWSProcessorProvider(ObjectFactory):
    def get_or_create(self, service, **kwargs):
        return self.create(service, **kwargs)


ml_platform_aws_processor = AWSProcessorProvider()
ml_platform_aws_processor.register_builder("SKLearnProcessor", SKLearnProcessorBuilder())


class AbstractTraining(ABC):
    """
    The Builder interface specifies methods for creating the different parts of
    the SageMaker Pipeline of Model Training objects.
    """

    @property
    @abstractmethod
    def pipeline(self) -> None:
        pass

    @abstractmethod
    def produce_paramters(self) -> None:
        """workflow Parameters"""
        pass

    @abstractmethod
    def produce_pre_process_data(self) -> None:
        """Feature Engineering"""
        pass

    @abstractmethod
    def produce_train(self) -> None:
        """Model Training"""
        pass

    @abstractmethod
    def produce_evaluation(self) -> None:
        """Model Evaluation"""
        pass

    @abstractmethod
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
        processor = ml_platform_aws_processor.get_or_create(
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


class TrainingApplication:
    def __init__(self) -> None:
        self._builder = None
        self._config = None

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config) -> None:
        self._config = config

    @property
    def builder(self) -> TrainingBuilder:
        return self._builder

    @builder.setter
    def builder(self, builder: TrainingBuilder) -> None:
        """
        The Director works with any builder instance that the client code passes
        to it. This way, the client code may alter the final type of the newly
        assembled product.
        """
        self._builder = builder

    """
    The Director can construct several product variations using the same
    building steps.
    """

    def build_minimal_viable_pipeline(self) -> None:
        logger.info("build minimal viable pipeline")

        logger.info("produce paramters")
        self.builder.produce_paramters(self._config.parameters)

        logger.info("produce pre_process_data")
        self.builder.produce_pre_process_data(self._config)

    def build_full_featured_pipeline(self) -> None:
        self.builder.produce_pre_process_data()
        self.builder.produce_train()
        self.builder.produce_evaluation()
        self.builder.produce_condition()


if __name__ == "__main__":
    args = {"service": "abalone", "context": "training"}

    builder_factory = {"training": TrainingBuilder()}
    pipeline_factory = {"training": TrainingApplication()}

    app = pipeline_factory.get(args["context"])
    app.builder = builder_factory.get(args["context"])
    app.config = settings.products[args["service"]][args["context"]]

    app.build_minimal_viable_pipeline()
    print(json.dumps(json.loads(app.builder.pipeline.definition()), indent=4))

    app.build_minimal_viable_pipeline()
    app.builder.pipeline.upsert(role_arn=sagemaker.get_execution_role())

    app.builder.pipeline.start()
