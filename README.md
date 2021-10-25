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

In your Github repo, go to settings, Secrets, and add 2 secrets with their respective credentials: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` . You will want to use a user that has the appropriate role to deploy a Lambda function and API Gateway using a CloudFormation template.

2. Push API Gateway and Lambda function to AWS

This repo has a built in CI/CD pipeline using Github Actions found in `.github/workflows/deploy.yml`. All developement branches should be built off the `dev` branch. Once the branch is pushed to the Github repo, a small amount of tests will run to ensure the code is working as intended. When the development branch gets merged into the `dev` branch, Github will deploy a dev version of the API Gateway and Lambda to AWS, with a naming convention of `dev` added to the name. Finally, when `dev` is merged into `main` the true production version of the application will be available for use.

3. Create the API Integration in Snowflake

This repo is primarily intended to deploy the API Gateway and Lambda to AWS. All other set up will need to take place in Snowflake. You will want to follow the [Snowflake documentation](https://docs.snowflake.com/en/sql-reference/external-functions-creating-aws-common-api-integration.html) describing the API Integration and the AWS IAM policy and role that is needed.

### TODO:
* Unittests