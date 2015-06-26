#!/bin/bash

VERSION=$(./version.sh)
EB_BUCKET=elasticbeanstalk-us-east-1-248182584102

# Deploy image to Docker Hub
docker login -e $DOCKER_EMAIL -u $DOCKER_USER -p $DOCKER_PASS
docker push dbhi/data-models-sqlalchemy:$VERSION

# Upload package to PyPi
sed -e "s/<PYPI_USER>/$PYPI_USER/" -e "s/<PYPI_PASS>/$PYPI_PASS/" \
    < .pypirc.template > .pypirc
python setup.py register
python setup.py sdist bdist_wheel
twine upload dist/*

# Create new Elastic Beanstalk version
DOCKERRUN_FILE=$VERSION-Dockerrun.aws.json
sed "s/<TAG>/$VERSION/" < Dockerrun.aws.json.template > $DOCKERRUN_FILE
aws s3 cp $DOCKERRUN_FILE s3://$EB_BUCKET/$DOCKERRUN_FILE
aws elasticbeanstalk create-application-version \
    --application-name data-models-sqlalchemy \
    --version-label $VERSION \
    --source-bundle S3Bucket=$EB_BUCKET,S3Key=$DOCKERRUN_FILE

# Update Elastic Beanstalk environment to new version
aws elasticbeanstalk update-environment \
    --environment-name data-model-sqlalchemy \
    --version-label $VERSION
