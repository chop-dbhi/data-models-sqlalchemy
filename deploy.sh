#!/bin/bash

if [ "${CIRCLECI}" = "true" ]; then
    export BUILD_NUM="${CIRCLE_BUILD_NUM}"
    export COMMIT_SHA1="${CIRCLE_SHA1}"
fi

VERSION=$(./version.sh)
EB_BUCKET=elasticbeanstalk-us-east-1-248182584102

# Push image to Docker Hub registry.
docker login -e $DOCKER_EMAIL -u $DOCKER_USER -p $DOCKER_PASS
docker push dbhi/data-models-sqlalchemy:${VERSION//+/-}

# Create new Elastic Beanstalk version.
DOCKERRUN_FILE=$VERSION-Dockerrun.aws.json
sed "s/<TAG>/${VERSION//+/-}/" < Dockerrun.aws.json.template > $DOCKERRUN_FILE
aws --region=us-east-1 s3 cp $DOCKERRUN_FILE s3://$EB_BUCKET/$DOCKERRUN_FILE
aws --region=us-east-1 elasticbeanstalk create-application-version \
    --application-name data-models-sqlalchemy \
    --version-label $VERSION \
    --source-bundle S3Bucket=$EB_BUCKET,S3Key=$DOCKERRUN_FILE

# Update dev deployment on Elastic Beanstalk.
aws --region=us-east-1 elasticbeanstalk update-environment \
    --environment-name data-models-sa-dev \
    --version-label $VERSION

# If final version...
if [ ${#VERSION} -lt 6 ]; then

    # Create GitHub release.
    git tag -a ${VERSION} -m "Release of version ${VERSION}"
    git push --tags

    # Upload package to PyPi.
    pip install wheel twine
    sed -e "s/<PYPI_USER>/$PYPI_USER/" -e "s/<PYPI_PASS>/$PYPI_PASS/" \
        < .pypirc.template > .pypirc
    python setup.py register
    python setup.py sdist bdist_wheel
    twine upload -u $PYPI_USER -p $PYPI_PASS dist/*

    # Update prod deployment on Elastic Beanstalk.
    aws --region=us-east-1 elasticbeanstalk update-environment \
        --environment-name data-models-sqlalchemy \
        --version-label $VERSION

fi
