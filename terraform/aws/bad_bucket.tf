resource "aws_s3_bucket" "bad_compliance_bucket" {
  bucket = "nis2-compliance-fail-test"
}
# MISSING: server_side_encryption_configuration (Violates NIS2 Art 21.2.f)
