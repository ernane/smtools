from __future__ import annotations

import json

import sagemaker

from smtools import logger
from smtools.app import SMTools

if __name__ == "__main__":
    args = {"service": "abalone", "context": "training"}

    smtools = SMTools()
    app = smtools.create_app(service=args.get("service"), context=args.get("context"))

    app.build_minimal_viable_pipeline()
    logger.info(json.dumps(json.loads(app.builder.pipeline.definition()), indent=2))

    app.build_minimal_viable_pipeline()
    app.builder.pipeline.upsert(role_arn=sagemaker.get_execution_role())

    # app.builder.pipeline.start()
