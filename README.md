## DRF-TDD-Example

An example Django REST framework project for test driven development.

### API Endpoints

#### Users

* GET **/api/users/** (Retrieve user info endpoint)
* PUT/PATCH **/api/users/** (Update user info endpoint)
* POST **/api/users/create/** (Create user endpoint)
* POST **/api/users/login/** (Login user endpoint)
* POST **/api/users/token_refresh/** (Refresh JWT token endpoint)

#### Todos

* GET **/api/todos/categories/** (Todo category list endpoint)
* POST **/api/todos/categories/** (Todo category create endpoint)
* PUT/PATCH **/api/todos/categories/{category-id}/** (Todo category update endpoint)
* DELETE **/api/todos/categories/{category-id}/** (Todo category destroy endpoint)

* GET **/api/todos/items/** (Todo items list endpoint)
* POST **/api/todos/items/** (Todo items create endpoint)
* GET **/api/todos/items/{item-id}/** (Todo items retrieve endpoint)
* PUT/PATCH **/api/todos/items/{item-id}/** (Todo items update endpoint)
* DELETE **/api/todos/items/{item-id}/** (Todo items destroy endpoint)

### Install 

    pip install pipenv
    pipenv install
    pipenv shell

### Usage

    python manage.py test
    python manage.py runserver
