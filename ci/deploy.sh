#!/bin/bash

DIRNAME="$(dirname $0)"
DIRNAME="$( cd ${DIRNAME} && pwd )"
cd "${DIRNAME}/../"
VERSION="$(${DIRNAME}/version.sh)"

echo "Pushing image to Docker Hub registry."
docker login -e "${DOCKER_EMAIL}" -u "${DOCKER_USER}" -p "${DOCKER_PASS}"
docker push "dbhi/${APP_NAME}:${VERSION//+/-}"

echo "Creating new Elastic Beanstalk version."
DOCKERRUN_FILE="${VERSION-Dockerrun.aws.json}"
sed "s/<TAG>/${VERSION//+/-}/" < "${DIRNAME}/Dockerrun.aws.json.template" > \
    "${DOCKERRUN_FILE}"
aws --region=us-east-1 s3 cp "${DOCKERRUN_FILE}" \
    "s3://${AWS_S3_BUCKET}/${DOCKERRUN_FILE}"
aws --region=us-east-1 elasticbeanstalk create-application-version \
    --application-name "${APP_NAME}" \
    --version-label "${VERSION}" \
    --source-bundle "S3Bucket=${AWS_S3_BUCKET},S3Key=${DOCKERRUN_FILE}"

# If commit is on master branch...
if [ "${BRANCH}" = "master" ]; then

    echo "Updating tip of development deployment on Elastic Beanstalk."
    AWS_ENV_NAME="${DEV_AWS_ENV_NAME}"
    aws --region=us-east-1 elasticbeanstalk update-environment \
        --environment-name "${AWS_ENV_NAME}" \
        --version-label "${VERSION}"

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
        AWS_ENV_NAME="${PROD_AWS_ENV_NAME}"
        aws --region=us-east-1 elasticbeanstalk update-environment \
            --environment-name "${AWS_ENV_NAME}" \
            --version-label "${VERSION}"
    
    fi

# If not on master branch...
else

    AWS_ENV_NAME="${PROD_AWS_ENV_NAME}-${BRANCH}"
    BRANCH_EXISTS=$(aws --region=us-east-1 elasticbeanstalk \
        describe-environments --application-name "${APP_NAME}" \
        --environment-name "${AWS_ENV_NAME}" | jq --raw-output \
        '.Environments | length')

    # If branch environment already exists...
    if [ "${BRANCH_EXISTS}" = 1 ]; then

        echo "Updating ${BRANCH} branch deployment on Elastic Beanstalk."
        aws --region=us-east-1 elasticbeanstalk update-environment \
            --environment-name "${AWS_ENV_NAME}" \
            --version-label "${VERSION}"

    # If branch environment doesn't exist yet...
    else

        echo "Creating new ${BRANCH} branch deployment on Elastic Beanstalk."

        # Set up postfix for send only email service.
        sudo apt-get update
        sudo debconf-set-selections <<< \
            "postfix postfix/mailname string `hostname`.circleci.com"
        sudo debconf-set-selections <<< \
            "postfix postfix/main_mailer_type string 'Internet Site'"
        sudo DEBIAN_FRONTEND=noninteractive apt-get -y install postfix
        sudo apt-get install -y mailutils

        # Send attempt notification email.
        TO_EMAILS=(${NOTIFICATION_EMAIL_ADDR})
        sed -e "s/<APP_NAME>/${APP_NAME}/" \
            -e "s/<AWS_ENV_NAME>/${AWS_ENV_NAME}/" \
            < "${DIRNAME}/before_create_env.eml.template" | \
            mail -s "New AWS ElasticBeanstalk Environment Creation Attemp" \
                -r "${NOTIFICATION_EMAIL_FROM}" \
                "${TO_EMAILS[@]}"

        # Create new AWS environment.
        aws --region=us-east-1 elasticbeanstalk create-environment \
            --application-name "${APP_NAME}" \
            --environment-name "${AWS_ENV_NAME}" \
            --cname-prefix "${AWS_ENV_NAME}" \
            --version-label "${VERSION}" \
            --template-name "${AWS_ENV_TEMPLATE}" \
            --tags "Key=billing:owner,Value=${BILLING_OWNER}" \
            "Key=billing:actcode,Value=${BILLING_ACTCODE}" \
            "Key=billing:description,Value=${BILLING_DESCRIPTION}"

    fi

fi

echo "Adding pending deploy status to GitHub commit with EB console URL."
AWSID=$(aws --region=us-east-1 elasticbeanstalk describe-environments \
    --application-name "${APP_NAME}" \
    --environment-name "${AWS_ENV_NAME}" | \
    jq --raw-output '.Environments[0].EnvironmentId')
sed -e "s/<AWSID>/${AWSID}/" < "${DIRNAME}/pending_status.json.template" > \
    status.json
curl -u "username:${GITHUB_TOKEN}" -X POST \
    -H "Content-Type: 'application/json'" -d @status.json \
    "https://api.github.com/repos/chop-dbhi/${APP_NAME}/statuses/${COMMIT_SHA1}"

AWSHEALTH="Grey"
while [ "${AWSHEALTH}" = "Grey" ]; do
    echo "Waiting for EB environment ${AWS_ENV_NAME} to deploy."
    echo "Current environment health is ${AWSHEALTH}."
    AWSHEALTH=$(aws --region=us-east-1 \
        elasticbeanstalk describe-environments \
        --application-name "${APP_NAME}" \
        --environment-name "${AWS_ENV_NAME}" | \
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
            "https://api.github.com/repos/chop-dbhi/${APP_NAME}/statuses/${COMMIT_SHA1}"
        ;;
    "Yellow")
        sed -e "s/<AWSID>/${AWSID}/" \
            < "${DIRNAME}/error_status.json.template" > status.json
        curl -u "username:${GITHUB_TOKEN}" -X POST \
            -H "Content-Type: 'application/json'" -d @status.json \
            "https://api.github.com/repos/chop-dbhi/${APP_NAME}/statuses/${COMMIT_SHA1}"
        ;;
    "Green")
        sed -e "s/<AWS_ENV_NAME>/${AWS_ENV_NAME}/" \
            < "${DIRNAME}/success_status.json.template" > status.json
        curl -u "username:${GITHUB_TOKEN}" -X POST \
            -H "Content-Type: 'application/json'" -d @status.json \
            "https://api.github.com/repos/chop-dbhi/${APP_NAME}/statuses/${COMMIT_SHA1}"
        ;;
esac

# If an AWS environment was created...
if [ "${BRANCH_EXISTS}" = 0 ]; then

    # Send a creation complete notification email.
    sed -e "s/<APP_NAME>/${APP_NAME}/" \
        -e "s/<AWS_ENV_NAME>/${AWS_ENV_NAME}/" \
        -e "s/<AWSHEALTH>/${AWSHEALTH}/" \
        < "${DIRNAME}/after_create_env.eml.template" | \
        mail -s "New AWS ElasticBeanstalk Environment Created" \
            -r "${NOTIFICATION_EMAIL_FROM}" \
            "${TO_EMAILS[@]}"

fi
