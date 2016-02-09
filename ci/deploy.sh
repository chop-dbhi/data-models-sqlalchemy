#!/bin/bash

# This script deploys a Dockerized python app image to Docker Hub, creates a
# running ElasticBeanstalk deployment on AWS, and, if the version is final,
# tags a release on GitHub and pushes the package to PyPi.
#
# If the commit is on master and the version is final, the script
# deploys the app to the production AWS environment. If the commit is on
# master with a non-final version, the dev AWS environment is used. If the
# commit is not on master, a branch-name-derived environment is created, if
# necessary, and used.
#
# Notifications about the status of deployments to AWS are sent to GitHub as
# commit statuses. Notifications about creation of new AWS environments are
# emailed.
#
# The following environment variables must be set in order for the script to
# succeed (use the environment variable project config on CircleCI):
#
# DOCKER_EMAIL, DOCKER_USER, and DOCKER_PASS to authenticate with Docker Hub.
# APP_NAME to identify the app on Docker Hub and also AWS EB.
# AWS_S3_BUCKET to identify the place where new AWS EB app version files
# should be uploaded.
# DEV_AWS_ENV_NAME and PROD_AWS_ENV_NAME to identify existing AWS EB envs.
# NOTIFICATION_EMAIL_ADDR and NOTIFICATION_EMAIL_FROM to specify email
# receivers (separated by spaces) and a sender, respectively.
# AWS_ENV_TEMPLATE to identify a template AWS env config for new AWS envs.
# BILLING_OWNER, BILLING_ACTCODE, and BILLING_DESCRIPTION to add billing tags
# to new AWS envs.
# GITHUB_TOKEN, which is a GitHub user auth token, in order to post commit
# statuses.
#
# The script was built to run on CircleCI, but could potentially be run in
# other environments, if the BRANCH, COMMIT_SHA1, and environment variables
# from circle.yml are set another way and the dependencies for circle.yml are
# installed in another way (this is untested advice).


# Get dirname of this script relative to runtime cwd.
DIRNAME="$(dirname $0)"
DIRNAME="$( cd ${DIRNAME} && pwd )"

# Change runtime cwd to parent directory.
cd "${DIRNAME}/../"

# Get app version.
VERSION="$(${DIRNAME}/version.sh)"

echo "Pushing image to Docker Hub registry."
docker login -e "${DOCKER_EMAIL}" -u "${DOCKER_USER}" -p "${DOCKER_PASS}"
docker push "dbhi/${APP_NAME}:${BRANCH_TAG}"

echo "Creating new Elastic Beanstalk version."
if [ ${#VERSION} -lt 6 ]; then
    docker push "dbhi/${APP_NAME}:${VERSION}"
    DOCKERRUN_FILE="${VERSION}-Dockerrun.aws.json"
    sed "s/<TAG>/${VERSION}/" < "${DIRNAME}/Dockerrun.aws.json.template" > \
        "${DOCKERRUN_FILE}"
else
    DOCKERRUN_FILE="${BRANCH_TAG}-Dockerrun.aws.json"
    sed "s/<TAG>/${BRANCH_TAG}/" < "${DIRNAME}/Dockerrun.aws.json.template" > \
        "${DOCKERRUN_FILE}"
fi
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

    echo "Checking for outdated branch deployments on Elastic Beanstalk."
    AWS_BRANCH_ENV_NAMES=$(aws --region=us-east-1 elasticbeanstalk \
        describe-environments --application-name "${APP_NAME}" | \
        jq --raw-output '.Environments | .[].EnvironmentName')
    GITHUB_BRANCH_NAMES=$(curl -u "username:${GITHUB_TOKEN}" -X GET \
        "https://api.github.com/repos/chop-dbhi/${APP_NAME}/branches" \
        2>/dev/null | jq --raw-output '.[].name')

    for AWS_BRANCH_ENV_NAME in ${AWS_BRANCH_ENV_NAMES}; do
        case "${AWS_BRANCH_ENV_NAME}" in
            "${PROD_AWS_ENV_NAME}")
                # Never remove prod environment.
                ;;
            "${DEV_AWS_ENV_NAME}")
                # Never remove tip of dev environment.
                ;;
            *)
                AWS_BRANCH="${AWS_BRANCH_ENV_NAME#$APP_NAME-}"
                GITHUB_BRANCH_EXISTS=0
                for GITHUB_BRANCH in ${GITHUB_BRANCH_NAMES}; do
                    if [ "${AWS_BRANCH}" = "${GITHUB_BRANCH}" ]; then
                        GITHUB_BRANCH_EXISTS=1
                    fi
                done
                if [ ${GITHUB_BRANCH_EXISTS} -eq 0 ]; then
                    echo "Removing outdated ${AWS_BRANCH} branch deployment on Elastic Beanstalk."
                    aws --region=us-east-1 elasticbeanstalk \
                        terminate-environment --environment-name \
                        "${AWS_BRANCH_ENV_NAME}"
                fi
                ;;
        esac
    done

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
