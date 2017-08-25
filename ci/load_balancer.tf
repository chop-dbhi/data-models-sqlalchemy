data "aws_acm_certificate" "default" {
  domain = "*.research.chop.edu"
}

resource "aws_alb" "public" {
  name            = "${var.workgroup}-${var.project}-public"
  subnets         = ["${data.terraform_remote_state.vpc.development_sandbox_vpc.public_subnets}"]
  security_groups = ["${aws_security_group.web_public.id}", "${aws_security_group.internal.id}"]

  tags {
    Name        = "${var.workgroup}-${var.project}-public"
    Workgroup   = "${var.workgroup}"
    Project     = "${var.project}"
  }
}

resource "aws_alb_target_group" "public" {
  name     = "${var.workgroup}-${var.project}-public"
  vpc_id   = "${data.terraform_remote_state.vpc.development_sandbox_vpc.id}"
  protocol = "HTTP"
  port     = 80

  health_check {
    path = "/"
    port = 80
  }

  tags {
    Name        = "${var.workgroup}-${var.project}-public"
    Workgroup   = "${var.workgroup}"
    Project     = "${var.project}"
  }
}

resource "aws_alb_listener" "public_https" {
  load_balancer_arn = "${aws_alb.public.arn}"
  port              = "443"
  certificate_arn   = "${data.aws_acm_certificate.default.arn}"
  protocol          = "HTTPS"

  default_action {
    target_group_arn = "${aws_alb_target_group.public.arn}"
    type             = "forward"
  }
}

resource "aws_alb_listener" "public_http" {
  load_balancer_arn = "${aws_alb.public.arn}"
  port              = "80"
  protocol          = "HTTP"

  default_action {
    target_group_arn = "${aws_alb_target_group.public.arn}"
    type             = "forward"
  }
}
