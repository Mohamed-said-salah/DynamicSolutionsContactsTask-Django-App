# Contact Manager
 - Building a Django app that authenticates users with JWT. And allow them to save contacts, search and edit them.
   Multi Contact update in the same time prevented by using Distributed Lock technique. And the app is containerized.

## Languages and frameworks 📑
 - Python 
 - Django
 - PostgreSQL 
 - Redis 
 - Docker

## Packages 🔎
 - DjangoRestFramework
 - drf-spectacular (API Documentation) 📃
 - Simple JWT
 
## Features 🥇
 - Distributed Lock 🔐
 - Search Contacts

## Models in The App 📋
 - User (id, username, email, password, is_admin)
 - Contact (id, contact_name, phone, email, created_by, updated_by)

## IDEs 💻
 - VS code
 - PyCharm

## Project Setup 💽
 - Clone this repository to your local machine and open the project by any IDE.

   ``` bash
   git https://github.com/Mohamed-said-salah/DynamicSolutionsContactTask.git
   cd contact_service
   ```
 - Run the following command to start the app.
   ``` bash
   docker compose up
   ```
   or 
   ``` bash
   docker-compose up
   ```

## Usage 🚀
 - Directly try it by nevigating to http://localhost:8000/api/swagger/ in your browser.
 - Here is the list of the API Endpoints
   * Users
     - Register new user
       ``` bash
       POST /api/users/register/
       ```
     - Login with user
       ``` bash
       POST /api/users/login/
       ```
   * Token
     - Refresh access token
       ``` bash
       POST /api/token/refresh/
       ```
   * Contacs
     - Create new Contact
       ``` bash
       POST /api/contacts/create/
       ```
     - Reserve contact editing session
       ``` bash
       GET /api/contacts/lock-edit/{id}/
       ```
     - Edit Contact
       ``` bash
       PUT /api/contacts/edit/{id}/{edit-session-token}/
       ```
     - Find contact by id
       ``` bash
       GET /api/contacts/detail/{id}/
       ```
     - Search contacts
       ``` bash
       GET /api/contacts/search/q?={search_keywords}
       ```  

<br>
<br>

## Projoect Exaple 🖼️

<div align='center'>
<img src="https://github.com/Mohamed-said-salah/DynamicSolutionsContactTask/blob/main/screen_shots/Screenshot%202024-01-12%20113838.png?raw=true">
<hr/>
</div>
