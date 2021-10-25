# Snowflake External Function For Translating Text

### Purpose

This repo contains the code to deploy an external function in Snowflake that can translate English text and return a JSON object containing translated text for each language that was requested.

### Example Call and Response in Snowflake

Example call in Snowflake:

```SQL

select translate_from_english('This is an example english text', array_construct('es','fr', 'ja'));

```

Example response:

```JSON
[
  {
    "language": "es",
    "status": "success",
    "translated_text": "Este es un ejemplo de texto en inglés"
  },
  {
    "language": "fr",
    "status": "success",
    "translated_text": "Voici un exemple de texte anglais."
  },
  {
    "language": "ja",
    "status": "success",
    "translated_text": "これは英語のテキストの例です"
  }
]

```

You can find a list of supported languages and language codes in [Amazon's documentation](https://docs.aws.amazon.com/translate/latest/dg/what-is.html#what-is-languages) for their AWS Translate service.

### How to Deploy

1. Set up Github Repo Settings

In your Github repo, go to settings, Secrets, and add 3 secrets with their respective credentials: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION`. You will want to use a user that has the appropriate role to deploy a Lambda function and API Gateway using a CloudFormation template.

2. Push API Gateway and Lambda function to AWS

This repo has a built in CI/CD pipeline using Github Actions found in `.github/workflows/deploy.yml`. All developement branches should be built off the `dev` branch. Once the branch is pushed to the Github repo, a small amount of tests will run to ensure the code is working as intended. When the development branch gets merged into the `dev` branch, Github will deploy a dev version of the API Gateway and Lambda to AWS, with a naming convention of `dev` added to the name. Finally, when `dev` is merged into `main` the true production version of the application will be available for use.

The branches should look similar to this flow:

```
           < feature_branch_1
           < feature_branch_2
main < dev < feature_branch_3
           < feature_branch_4
           < feature_branch_5
```

3. Create the API Integration in Snowflake

This repo is primarily intended to deploy the API Gateway and Lambda to AWS. All other set up will need to take place in Snowflake. You will want to follow the [Snowflake documentation](https://docs.snowflake.com/en/sql-reference/external-functions-creating-aws-common-api-integration.html) describing the API Integration and the AWS IAM policy and role that is needed.

4. Create the Snowflake External Function in Snowflake

Here is an example of creating and calling the external function in Snowflake:

```SQL
create or replace external function translate_from_english(english_text varchar, languages variant)
    returns variant
    api_integration = <your_api_integration_name>
    as 'https://abc123ef5.execute-api.us-west-2.amazonaws.com/prod/translate/from_english';

select translate_from_english('This is an example english text', array_construct('es','fr', 'ja'));

```


### Explanation of Files
* `.github/workflows/deploy.yml`: Uses Github Actions for the CI/CD pipeline
* `requirements.txt`: Lists the required packages needed to run the code locally and deploy to Lambda. You can run `pip install -r requirements.txt` on your local environment to download the required packages for your local development use
* `serverless.yml`: Uses the serverless framework to deploy API Gateway and Lambda to AWS. See `.github/workflows/deploy.yml` for the code that runs to deploy with serverless.
* `tests.py`: Unittests that must pass before the code gets deployed
* `translate_from_english.py`: This is the actual Python code that will run on the Lambda function


