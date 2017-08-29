output "external_dns_name" {
  value = "${aws_alb.public.dns_name}"
}
