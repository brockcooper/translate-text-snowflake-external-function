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

In Dev:

1. Push API Gateway and Lambda function to AWS
2. Create the API Integration in Snowflake
3. Deploy the Snowflake Terraform

### TODO

* Snowflake Terraform to build out Function and API Integration
* AWS Terraform for building out Policy, Role, External Integration
* GiHub Pipelines and environment variables
* Unittests