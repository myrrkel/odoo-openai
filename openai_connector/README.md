 [![License: AGPL-3](https://img.shields.io/badge/licence-AGPL--3-blue.png)](http://www.gnu.org/licenses/agpl-3.0-standalone.html)

OpenAI Connector
=================

[<img src="./static/img/openai_logo.svg" alt="OpenAI Logo" style="width:300px;"/>](https://openai.com/)

This module adds a connector for OpenAI API and brings the power of ChatGPT and DALL-E into Odoo.

To create a custom OpenAI Completion, Edit or Image, check how to set properly API parameters : [API Documentation](https://beta.openai.com/docs/api-reference/introduction)

## Configuration

Create an account on [https://beta.openai.com/](https://beta.openai.com/)

Create your API Key: [API keys](https://beta.openai.com/account/api-keys)

In **Settings**, fill the **API Key** field:

![image](./static/img/settings.png)

## Usage

### OpenAI Completion

To create a new **OpenAI Completion**, go to **Settings**, **Technical**, **OpenAI Completion** and create a new record.

![image](./static/img/completion_params.png)

**Model**: The model on witch the completion will be applied.

**Target Field**: The field where the generated value will be saved.

**Domain**: The domain to select the records on witch the completion will be run.


![image](./static/img/openai_params.png)

Check the [API Documentation](https://beta.openai.com/docs/api-reference/introduction) to set **OpenAI Parameters** values.

For Completion results go to **Settings**, **Technical**, **OpenAI Completion Results**

### OpenAI Edit

To create a new **OpenAI Edit**, go to **Settings**, **Technical**, **OpenAI Edit** and create a new record.

For results go to **Settings**, **Technical**, **OpenAI Edit Results**

### OpenAI Image

To create a new **OpenAI Image**, go to **Settings**, **Technical**, **OpenAI Image** and create a new record.

For results go to **Settings**, **Technical**, **OpenAI Image Results**

### Prompt template

Write a prompt template in Qweb:

![image](./static/img/prompt.png)

### Tests

Test actions use the first record selected by the domain.

Test first your prompt to adjust your template, then test the result of the Completion, Edit or Image to adjust OpenAI parameters.

![image](./static/img/tests.png)

## Requirements

This module requires the Python client library for OpenAI API

    pip install openai

## Maintainer

* This module is maintained by [Myrrkel](https://github.com/myrrkel). 
* Contact me on [LinkedIn](https://www.linkedin.com/in/michel-perrocheau-ba17a4122). 

[<img src="./static/description/logo.png" style="width:200px;"/>](https://github.com/myrrkel)



