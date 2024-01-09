 [![License: AGPL-3](https://img.shields.io/badge/licence-AGPL--3-blue.png)](http://www.gnu.org/licenses/agpl-3.0-standalone.html)

OpenAI Product Description
==========================

[<img src="./static/img/openai_logo.svg" alt="OpenAI Logo" style="width:300px;"/>](https://openai.com/)

This module allows to generate a product sales description with OpenAI's GTP3 model from product tags, attributes or any other product information.

## Usage

On a product, select **Create Sales Description** action :

![image](./static/img/create_description_action.png)

OpenAI will create 4 description proposals. Choose the one you prefer (you can correct it), then, click on **Apply** to save the value as the product sales description.

![image](./static/img/results.png)

This action is also available from the product list view.



## Requirements

[openai_connector](../openai_connector/README.md) is required. 

This module requires the Python client library for OpenAI API

    pip install openai

## Maintainer

* This module is maintained by [Michel Perrocheau](https://github.com/myrrkel). 
* Contact me on [LinkedIn](https://www.linkedin.com/in/michel-perrocheau-ba17a4122). 

[<img src="./static/description/logo.png" style="width:200px;"/>](https://github.com/myrrkel)



