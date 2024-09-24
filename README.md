<h1 align="center">Warehouse API</h1>


<img src="https://img.shields.io/badge/python3.12-blue">
<img src="https://img.shields.io/badge/FastAPI-blue">
<img src="https://img.shields.io/badge/PostgreSQL-blue">
<img src="https://img.shields.io/badge/Docker-blue">



## Description
Python realisation of simple warehouse api.

## Implemented:

- Add product
- Delete product
- Edit product
- Get list of all products
- Get product by id
- Create order with one or several products
- Get list of all orders
- Get order by id
- Change order status


Api documentation accessible by:

    http://hostaddress/docs
    http://hostaddress/redoc

Change 'hostaddress' to ip of host running project.

## Setup enviroment variables
### This operation is required!!!

Copy or rename '.tempate' file to .env file in the 'envs' directory. Then fill it with your values.

## Running

    docker-compose up -d

For development and testing:

    pip install -r requirements_dev.txt
    docker-compose -f docker-compose-dev.yaml up -d