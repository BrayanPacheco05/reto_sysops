import sys
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql.functions import col, to_timestamp
from awsglue.utils import getResolvedOptions


args = getResolvedOptions(
    sys.argv,
    ["JOB_NAME", "SOURCE_PATH", "TARGET_PATH"]
)

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args["JOB_NAME"], args)


source_path = args["SOURCE_PATH"]
target_path = args["TARGET_PATH"]


df = spark.read.json(source_path)


df = (
    df
    .select(
        "event_id",
        "timestamp",
        "user_id",
        "transaction_id",
        "amount",
        "currency",
        "status",
        "payment_method"
    )
    .withColumn(
        "timestamp",
        to_timestamp(col("timestamp"))
    )
    .withColumn(
        "amount",
        col("amount").cast("double")
    )
    .dropDuplicates(["event_id"])
    .dropna(
        subset=[
            "event_id",
            "timestamp",
            "user_id",
            "transaction_id",
            "amount"
        ]
    )
)


df.write \
    .mode("append") \
    .format("parquet") \
    .partitionBy("status") \
    .save(target_path)


job.commit()
