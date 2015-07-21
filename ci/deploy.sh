#!/bin/bash

DIRNAME="$(dirname $0)"
DIRNAME="$( cd ${DIRNAME} && pwd )"
cd "${DIRNAME}/../"
VERSION="$(${DIRNAME}/version.sh)"
EB_BUCKET=elasticbeanstalk-us-east-1-248182584102

echo "Pushing image to Docker Hub registry."
docker login -e "${DOCKER_EMAIL}" -u "${DOCKER_USER}" -p "${DOCKER_PASS}"
docker push "dbhi/data-models-sqlalchemy:${VERSION//+/-}"

echo "Creating new Elastic Beanstalk version."
DOCKERRUN_FILE="${VERSION-Dockerrun.aws.json}"
sed "s/<TAG>/${VERSION//+/-}/" < "${DIRNAME}/Dockerrun.aws.json.template" > \
    "${DOCKERRUN_FILE}"
aws --region=us-east-1 s3 cp "${DOCKERRUN_FILE}" \
    "s3://${EB_BUCKET}/${DOCKERRUN_FILE}"
aws --region=us-east-1 elasticbeanstalk create-application-version \
    --application-name data-models-sqlalchemy \
    --version-label "${VERSION}" \
    --source-bundle "S3Bucket=${EB_BUCKET},S3Key=${DOCKERRUN_FILE}"

# If commit is on master branch...
if [ "${BRANCH}" = "master" ]; then

    echo "Updating tip of development deployment on Elastic Beanstalk."
    AWSNAME="dmsa-dev"
    aws --region=us-east-1 elasticbeanstalk update-environment \
        --environment-name "${AWSNAME}" \
        --version-label $VERSION

    # If final version...
    if [ ${#VERSION} -lt 6 ]; then
    
        echo "Creating GitHub release."
        git config --global user.email "aaron0browne@gmail.com"
        git config --global user.name "Aaron Browne"
        git tag -a "${VERSION}" -m "Release of version ${VERSION}"
        git push --tags
    
        echo "Uploading package to PyPi."
        sed -e "s/<PYPI_USER>/${PYPI_USER}/" \
            -e "s/<PYPI_PASS>/${PYPI_PASS}/" \
            < "${DIRNAME}/.pypirc.template" > .pypirc
        python setup.py register
        python setup.py sdist bdist_wheel
        twine upload -u "${PYPI_USER}" -p "${PYPI_PASS}" dist/*
    
        echo "Updating production deployment on Elastic Beanstalk."
        AWSNAME="dmsa"
        aws --region=us-east-1 elasticbeanstalk update-environment \
            --environment-name "${AWSNAME}" \
            --version-label "${VERSION}"
    
    fi

# If not on master branch...
else

    AWSNAME="dmsa-${BRANCH}"
    BRANCH_EXISTS=$(aws --region=us-east-1 elasticbeanstalk \
        describe-environments --application-name data-models-sqlalchemy \
        --environment-name "${AWSNAME}" | jq --raw-output \
        '.Environments | length')

    # If branch environment already exists...
    if [ "${BRANCH_EXISTS}" = 1 ]; then

        echo "Updating ${BRANCH} branch deployment on Elastic Beanstalk."
        aws --region=us-east-1 elasticbeanstalk update-environment \
            --environment-name "${AWSNAME}" \
            --version-label "${VERSION}"

    # If branch environment doesn't exist yet...
    else

        echo "Creating new ${BRANCH} branch deployment on Elastic Beanstalk."
        aws --region=us-east-1 elasticbeanstalk create-environment \
            --application-name data-models-sqlalchemy \
            --environment-name "${AWSNAME}" \
            --cname-prefix "${AWSNAME}" \
            --version-label "${VERSION}" \
            --template-name data-models-sa-conf

    fi

fi

echo "Adding pending deploy status to GitHub commit with EB console URL."
AWSID=$(aws --region=us-east-1 elasticbeanstalk describe-environments \
    --application-name data-models-sqlalchemy \
    --environment-name "${AWSNAME}" | \
    jq --raw-output '.Environments[0].EnvironmentId')
sed -e "s/<AWSID>/${AWSID}/" < "${DIRNAME}/pending_status.json.template" > \
    status.json
curl -u "username:${GITHUB_TOKEN}" -X POST \
    -H "Content-Type: 'application/json'" -d @status.json \
    "https://api.github.com/repos/chop-dbhi/data-models-sqlalchemy/statuses/${COMMIT_SHA1}"

AWSHEALTH="Grey"
while [ "${AWSHEALTH}" = "Grey" ]; do
    echo "Waiting for EB environment ${AWSNAME} to deploy."
    echo "Current environment health is ${AWSHEALTH}."
    AWSHEALTH=$(aws --region=us-east-1 \
        elasticbeanstalk describe-environments \
        --application-name data-models-sqlalchemy \
        --environment-name "${AWSNAME}" | \
        jq --raw-output '.Environments[0].Health')
    sleep 30
done

echo "Updating the GitHub deploy status."
echo "Current environment health is ${AWSHEALTH}."
case "${AWSHEALTH}" in
    "Red")
        sed -e "s/<AWSID>/${AWSID}/" \
            < "${DIRNAME}/fail_status.json.template" > status.json
        curl -u "username:${GITHUB_TOKEN}" -X POST \
            -H "Content-Type: 'application/json'" -d @status.json \
            "https://api.github.com/repos/chop-dbhi/data-models-sqlalchemy/statuses/${COMMIT_SHA1}"
        ;;
    "Yellow")
        sed -e "s/<AWSID>/${AWSID}/" \
            < "${DIRNAME}/error_status.json.template" > status.json
        curl -u "username:${GITHUB_TOKEN}" -X POST \
            -H "Content-Type: 'application/json'" -d @status.json \
            "https://api.github.com/repos/chop-dbhi/data-models-sqlalchemy/statuses/${COMMIT_SHA1}"
        ;;
    "Green")
        sed -e "s/<AWSNAME>/${AWSNAME}/" \
            < "${DIRNAME}/success_status.json.template" > status.json
        curl -u "username:${GITHUB_TOKEN}" -X POST \
            -H "Content-Type: 'application/json'" -d @status.json \
            "https://api.github.com/repos/chop-dbhi/data-models-sqlalchemy/statuses/${COMMIT_SHA1}"
        ;;
esac
