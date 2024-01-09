 [![License: AGPL-3](https://img.shields.io/badge/licence-AGPL--3-blue.png)](http://www.gnu.org/licenses/agpl-3.0-standalone.html)

OpenAI Edit Product Image
=========================

[<img src="./static/img/openai_logo.svg" alt="OpenAI Logo" style="width:300px;"/>](https://openai.com/)

This module allows to generate a new product image from a cropped product image with DALL-E.

## Usage

On a product, select **DALL-E** tab, add a PNG image with transparency or add a mask image, and write a description of the result you want:

You can also set an image ratio.

![image](./static/img/config_product.png)

Go in menu **Action** and select **Edit Product Image with DALL-E**:

![image](./static/img/product_results.png)

Select the image you prefer and click on **Apply Image** to set is as product image :

![image](./static/img/apply_image.png)

![image](./static/img/product.png)



Action **Edit Product Image with DALL-E** is also available from the product list view.

## Create a product image from scratch

Leave the **Source Image** field empty, select **Edit Product Image with DALL-E** action.

This option will turn any product into a DALL-E playground...

*<sub>You can also update the template "edit_product_image_template" to create your own prompt from your product properties.</sub>*



![image](./static/img/create_image_prompt.png)
![image](./static/img/create_image.png)




## Requirements

[openai_connector](../openai_connector/README.md) is required. 

This module requires the Python client library for OpenAI API

    pip install openai

## Maintainer

* This module is maintained by [Michel Perrocheau](https://github.com/myrrkel). 
* Contact me on [LinkedIn](https://www.linkedin.com/in/michel-perrocheau-ba17a4122). 

[<img src="./static/description/logo.png" style="width:200px;"/>](https://github.com/myrrkel)



