resource "aws_glue_catalog_database" "main" {
  name        = replace("${local.name}_catalog", "-", "_")
  description = "Catalog for reto sysops medallion architecture"
}

resource "aws_glue_catalog_table" "transactions" {
  name          = "transactions"
  database_name = aws_glue_catalog_database.main.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    classification = "parquet"
    typeOfData     = "file"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.data.id}/silver/transactions/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "event_id"
      type = "string"
    }

    columns {
      name = "timestamp"
      type = "timestamp"
    }

    columns {
      name = "user_id"
      type = "string"
    }

    columns {
      name = "transaction_id"
      type = "string"
    }

    columns {
      name = "amount"
      type = "double"
    }

    columns {
      name = "currency"
      type = "string"
    }

    columns {
      name = "payment_method"
      type = "string"
    }
  }

  partition_keys {
    name = "status"
    type = "string"
  }
}

resource "aws_glue_job" "bronze_to_silver" {
  name     = "${local.name}-bronze-to-silver"
  role_arn = aws_iam_role.glue.arn

  glue_version = "4.0"

  worker_type       = "G.1X"
  number_of_workers = 2

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.data.bucket}/scripts/bronze_to_silver.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language" = "python"

    "--SOURCE_PATH" = "s3://${aws_s3_bucket.data.bucket}/bronze/"

    "--TARGET_PATH" = "s3://${aws_s3_bucket.data.bucket}/silver/transactions/"

    "--enable-metrics" = "true"

    "--enable-continuous-cloudwatch-log" = "true"

    "--enable-spark-ui" = "true"

    "--spark-event-logs-path" = "s3://${aws_s3_bucket.data.bucket}/spark-logs/"
  }

  execution_property {
    max_concurrent_runs = 1
  }

  timeout = 10
}
