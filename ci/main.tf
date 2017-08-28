provider "aws" {
  profile = "${var.profile}"
  region  = "${var.region}"
}

data "terraform_remote_state" "vpc" {
  backend     = "s3"
  environment = "${var.vpc_remote_state_environment}"

  config {
    profile = "${var.profile}"
    region  = "${var.region}"
    bucket  = "${var.vpc_remote_state_bucket}"
    key     = "${var.vpc_remote_state_key}"
  }
}

data "aws_ami" "ecs" {
  most_recent = "true"
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn-ami*amazon-ecs-optimized"]
  }
}

data "template_file" "init" {
  template = "${file("init.sh")}"

  vars {
    tag = "${var.image_tag}"
  }
}

resource "aws_instance" "default" {
  subnet_id              = "${data.terraform_remote_state.vpc.development_sandbox_vpc.public_subnets[0]}"
  vpc_security_group_ids = ["${aws_security_group.ssh_access.id}", "${aws_security_group.internal.id}"]
  ami                    = "${data.aws_ami.ecs.id}"
  instance_type          = "${var.instance_type}"
  monitoring             = "true"
  key_name               = "${var.ssh_key_name}"
  user_data              = "${data.template_file.init.rendered}"

  tags {
    Name      = "${var.workgroup}-${var.project}"
    Workgroup = "${var.workgroup}"
    Project   = "${var.project}"
  }
}

resource "aws_alb_target_group_attachment" "default" {
  target_group_arn = "${aws_alb_target_group.public.arn}"
  target_id        = "${aws_instance.default.id}"
  port             = 80
}
