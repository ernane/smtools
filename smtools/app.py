# import json

# import sagemaker
# from sagemaker.workflow.pipeline import Pipeline

# from smtools.ext.services.abalone.pipelines.training import parameters, steps


# def create_app(name: str = "pipeline") -> Pipeline:
#     """Create a Pipeline app
#     Returns:
#         Pipeline: Instance of Pipeline
#     """
#     app = Pipeline(name=name)

#     return app


# if __name__ == "__main__":
#     pipeline = create_app("abalone")

#     parameters.init_app(pipeline)
#     steps.init_app(pipeline)

#     print(json.dumps(json.loads(pipeline.definition()), indent=4))

#     pipeline.upsert(role_arn=sagemaker.get_execution_role())

#     # execution = pipeline.start()

from smtools.ext.core.builder import TrainingBuilder
from smtools.ext.settings.config import settings
from smtools.ext.workflows.training import Training


class SMTools:
    def __init__(self) -> None:
        self.builders = {"training": TrainingBuilder()}
        self.workflows = {"training": Training()}

    def create_app(self, service, context):
        app = self.workflows.get(context)
        app.builder = self.builders.get(context)
        app.config = settings.products[service][context]
        return app
