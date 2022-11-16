# if __name__ == "__main__":
#     # print(settings.services.abalone.pipelines.training.parameters)
#     pipeline = create_app("abalone")

#     parameters.init_app(pipeline)
#     steps.init_app(pipeline)

#     print(json.dumps(json.loads(pipeline.definition()), indent=4))

#     pipeline.upsert(role_arn=sagemaker.get_execution_role())

#     execution = pipeline.start()


#     print(BASE_DIR)
#     #
#     data_raw = os.path.join(BASE_DIR, "data", "raw", "house_pricing.csv")
#     sess = sagemaker.Session()
#     s3_prefix = "mlops-workshop"
#     default_bucket = "datarocket-stg-sagemaker"
#     output_path = f"s3://{default_bucket}/{s3_prefix}/data/sm_processed"
#     raw_data_s3_prefix = "{}/data/raw".format(s3_prefix)
#     raw_s3 = sess.upload_data(path=data_raw, key_prefix=raw_data_s3_prefix)

#     #
#     session = PipelineSession(default_bucket=default_bucket)
#     role_arn = sagemaker.get_execution_role()
#     src_dir = os.path.join(
#         BASE_DIR,
#         "ext",
#         "services",
#         "synthetic_housing",
#         "src",
#     )

#     #
#     pipeline = create_app("synthetic-housing")

#     """
#     Patameters
#     """
#     processing_instance_count = ParameterInteger(
#         name="ProcessingInstanceCount", default_value=1
#     )

#     processing_instance_type = ParameterString(
#         name="ProcessingInstanceType", default_value="ml.m5.xlarge"
#     )

#     pipeline.parameters.append(processing_instance_count)
#     pipeline.parameters.append(processing_instance_type)
#     """
#     Patameters
#     """

#     preprocess_data_processor = SKLearnProcessor(
#         framework_version="0.23-1",
#         role=role_arn,
#         instance_type=processing_instance_type,
#         instance_count=processing_instance_count,
#         base_job_name="preprocess-data",
#         sagemaker_session=session,
#     )

#     preprocess_dataset_step = ProcessingStep(
#         name="PreprocessData",
#         code=os.path.join(src_dir, "train", "preprocessing.py"),
#         processor=preprocess_data_processor,
#         inputs=[
#             ProcessingInput(
#                 input_name="raw",
#                 source=raw_s3,
#                 destination="/opt/ml/processing/input",
#                 s3_data_distribution_type="ShardedByS3Key",
#             )
#         ],
#         outputs=[
#             ProcessingOutput(
#                 output_name="train",
#                 destination=f"{output_path}/train",
#                 source="/opt/ml/processing/train",
#             ),
#             ProcessingOutput(
#                 output_name="validation",
#                 destination=f"{output_path}/validation",
#                 source="/opt/ml/processing/validation",
#             ),
#             ProcessingOutput(
#                 output_name="test",
#                 destination=f"{output_path}/test",
#                 source="/opt/ml/processing/test",
#             ),
#         ],
#     )

#     pipeline.steps.append(preprocess_dataset_step)

#     print(json.dumps(json.loads(pipeline.definition()), indent=4))
