# Data Models Sqlalchemy Deployment

The service is currently deployed to AWS and available at [https://data-models-sqlalchemy.research.chop.edu/](https://data-models-sqlalchemy.research.chop.edu/). The deployment is designed for simplicity, but should also meet the current (low) availability requirements.

## Terraform Configuration

Using Terraform, this configuration deploys `data-models-sqlalchemy` into the CHOP Dev AWS VPC, as configured in `main.tf`. Also in `main.tf`, an EC2 instance is configured based on the Amazon Linux Elastic Container Service optimized image (which comes with Docker installed). It is deployed into a public subnet, for simplicity, since it contains no sensitive information, and provided with a user data initialization script that pulls the `data-models-sqlalchemy` image and runs a container from it. This script is rendered from the `init.sh` template with the injected image tag variable.

The final configuration in `main.tf` registers the EC2 instance in a load balancer target, configured in `load_balancer.tf`. A public load balancer, with both HTTP and HTTPS listeners that pass traffic to that target group, is also configured in `load_balancer.tf`. The `*.research.chop.edu` certificate is attached to the HTTPS listener. The load balancer is configured to prevent its destruction via command line, because its public DNS name is used to configure the external CNAME record which directs traffic to the service. This CNAME record was created by CHOP IS in response to an IS Request.

The load balancer and the EC2 instance are both in an internal security group, so they can communicate with each other. Only the load balancer is in a security group that allows public access to ports 80 and 443 for HTTP and HTTPS traffic, while only the EC2 instance is in a security group that allows SSH access on port 22 from IP addresses in the CHOP private network CIDR block. These three security groups are all configured in `security_groups.tf`.

## Potential Improvements

- Automate image creation
- Reduce redeployment downtime

## Cookbook

Following are some recipes to accomplish particular tasks or deal with certain situations in this `data-models-sqlalchemy` deployment. They all assume that you have valid AWS credentials for the CHOP Dev VPC. The best way to acquire those credentials is via the [`chopaws`](https://github.research.chop.edu/devops/aws-auth-cli) script.

### Build

Before deploying a new version of the application, you need to build a new docker image that contains that new version. First, if the version number has not been increased, edit `dmsa/__init__.py` to do that. Then, substituting in the correct version number as a tag, run `docker build -t dbhi/data-models-sqlalchemy:{{version}} .`.

### Push

After building a new image, you need to push it to the docker hub repository so that the EC2 instance will be able to pull it on initialization. This assumes you have already created a [Docker Hub](https://hub.docker.com/) account and that account has permission to push to the `dbhi/data-models-sqlalchemy` repository. First, log in to Docker Hub by executing `docker login` and entering your credentials at the prompt. Second, push the image, substituting the correct version number as a tag, with `docker push dbhi/data-models-sqlalchemy:{{version}}`.

### Deploy

After a new image has been built and pushed, you can deploy it using [Terraform](https://www.packer.io/downloads.html). First, edit `terraform.tfvars` to use the correct version number as the image tag. Then, generate a plan for the deployment via `terraform plan`. It's important to keep in mind that in this configuration, deploying a new version will destroy and recreate the EC2 instance, causing a brief downtime in the service. Once you've examined the plan and determined it to be satisfactory, you can apply the changes with `terraform apply`. (Note that this actually builds a new plan in memory before applying, so it may be prudent to implement a workflow change to actually guarantee planned change application, at some point.)
