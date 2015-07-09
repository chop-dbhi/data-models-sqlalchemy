#!/bin/bash

VERSION=$(./version.sh)
EB_BUCKET=elasticbeanstalk-us-east-1-248182584102

# Push image to Docker Hub registry.
docker login -e "${DOCKER_EMAIL}" -u "${DOCKER_USER}" -p "${DOCKER_PASS}"
docker push "dbhi/data-models-sqlalchemy:${VERSION//+/-}"

# Create new Elastic Beanstalk version.
DOCKERRUN_FILE=$VERSION-Dockerrun.aws.json
sed "s/<TAG>/${VERSION//+/-}/" < Dockerrun.aws.json.template > \
    "${DOCKERRUN_FILE}"
aws --region=us-east-1 s3 cp "${DOCKERRUN_FILE}" \
    "s3://${EB_BUCKET}/${DOCKERRUN_FILE}"
aws --region=us-east-1 elasticbeanstalk create-application-version \
    --application-name data-models-sqlalchemy \
    --version-label "${VERSION}" \
    --source-bundle "S3Bucket=${EB_BUCKET},S3Key=${DOCKERRUN_FILE}"

# Create new Elastic Beanstalk environment running new version.
AWSNAME="dmsa-${COMMIT_SHA1:0:8}"
aws --region=us-east-1 elasticbeanstalk create-environment \
    --application-name data-models-sqlalchemy \
    --environment-name "${AWSNAME}" \
    --cname-prefix "${AWSNAME}" \
    --version-label "${VERSION}" \
    --template-name data-models-sa-conf

# Add deployment URL to commit status.
curl -u "username:${GITHUB_TOKEN}" -X POST \
    -H "Content-Type: 'application/json'" -d '{"state": "success", \
    "target_url": "${AWSNAME}.elasticbeanstalk.com", \
    "description": "Deployed to AWS for review!", "context": "ci/custom"}' \
    "https://api.github.com/repos/chop-dbhi/data-models-sqlalchemy/statuses/${COMMIT_SHA1}"

# If commit is on master branch...
if [ "${BRANCH}" = "master" ]; then

    # Update release candidate deployment on Elastic Beanstalk.
    aws --region=us-east-1 elasticbeanstalk update-environment \
        --environment-name dmsa-dev \
        --version-label $VERSION

fi

# If final version...
if [ ${#VERSION} -lt 6 ]; then

    # Create GitHub release.
    git tag -a "${VERSION}" -m "Release of version ${VERSION}"
    git push --tags

    # Upload package to PyPi.
    sed -e "s/<PYPI_USER>/${PYPI_USER}/" -e "s/<PYPI_PASS>/${PYPI_PASS}/" \
        < .pypirc.template > .pypirc
    python setup.py register
    python setup.py sdist bdist_wheel
    twine upload -u "${PYPI_USER}" -p "${PYPI_PASS}" dist/*

    # Update prod deployment on Elastic Beanstalk.
    aws --region=us-east-1 elasticbeanstalk update-environment \
        --environment-name dmsa \
        --version-label "${VERSION}"

fi
