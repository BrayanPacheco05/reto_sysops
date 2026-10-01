import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, to_timestamp


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


print(f"Reading Bronze data from: {source_path}")

df = spark.read.json(source_path)

print(f"Bronze records read: {df.count()}")


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
    .dropna(
        subset=[
            "event_id",
            "timestamp",
            "user_id",
            "transaction_id",
            "amount",
            "status"
        ]
    )
    .dropDuplicates(["event_id"])
)


print(f"Valid unique records: {df.count()}")


(
    df.write
    .mode("overwrite")
    .format("parquet")
    .partitionBy("status")
    .save(target_path)
)


print(f"Silver data written to: {target_path}")

job.commit()
