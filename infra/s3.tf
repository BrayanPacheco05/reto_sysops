resource "aws_s3_bucket" "data" {
  bucket_prefix = "${local.name}-data-"
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_object" "bronze_folder" {
  bucket  = aws_s3_bucket.data.id
  key     = "bronze/"
  content = ""
}

resource "aws_s3_object" "silver_folder" {
  bucket  = aws_s3_bucket.data.id
  key     = "silver/"
  content = ""
}

resource "aws_s3_object" "gold_folder" {
  bucket  = aws_s3_bucket.data.id
  key     = "gold/"
  content = ""
}

resource "aws_s3_object" "scripts_folder" {
  bucket  = aws_s3_bucket.data.id
  key     = "scripts/"
  content = ""
}

resource "aws_s3_object" "athena_folder" {
  bucket  = aws_s3_bucket.data.id
  key     = "athena-results/"
  content = ""
}
