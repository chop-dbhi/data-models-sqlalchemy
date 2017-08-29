resource "aws_security_group" "web_public" {
  name        = "${var.workgroup}-${var.project}-web_public"
  description = "Allows all inbound traffic on ports 80 and 443 and all outbound traffic."
  vpc_id      = "${data.terraform_remote_state.vpc.development_sandbox_vpc.id}"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
    Name      = "${var.workgroup}-${var.project}-web_public"
    Workgroup = "${var.workgroup}"
    Project   = "${var.project}"
  }
}

resource "aws_security_group" "ssh_access" {
  name        = "${var.workgroup}-${var.project}-ssh_access"
  description = "Allows SSH access from the CHOP network CIDR."
  vpc_id      = "${data.terraform_remote_state.vpc.development_sandbox_vpc.id}"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.private_cidr}"]
  }

  egress {
    from_port   = "0"
    to_port     = "0"
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
    Name      = "${var.workgroup}-${var.project}-ssh_access"
    Workgroup = "${var.workgroup}"
    Project   = "${var.project}"
  }
}

resource "aws_security_group" "internal" {
  name        = "${var.workgroup}-${var.project}-internal"
  description = "Allows the load balancer to talk to the instance."
  vpc_id      = "${data.terraform_remote_state.vpc.development_sandbox_vpc.id}"

  ingress {
    from_port = "0"
    to_port   = "0"
    protocol  = "-1"
    self      = "true"
  }

  egress {
    from_port   = "0"
    to_port     = "0"
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
    Name      = "${var.workgroup}-${var.project}-internal"
    Workgroup = "${var.workgroup}"
    Project   = "${var.project}"
  }
}
