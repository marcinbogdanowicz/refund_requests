# Refund request processing system

This repo contains a refund request processing system. 

Main functionalities:
- [Account management](#account-management) - creation and user authentication, password resetting
- [Refund requests UI](#refund-requests-ui) - creation and listing
- [Refund requests management via admin site](#admin-site)
- [IBAN validation](#iban-validation)
- [Email emission system](#email-emission-system)
- [Secrets management with environment variables](#notes-on-envexample)

Main tech stack:
- Django 5.1
- Django REST Framework 3.15
- PostgreSQL
- Redis
- Mailpit for development

Frontend:
- Bootstrap 5.3
- JavaScript
- Axios

There are **two installation variants** available:
- [dockerized](#dockerized-installation)
- [direct (without Docker)](#installation-without-docker)

## Installation

### Dockerized installation 

> [!IMPORTANT]
> [Docker](https://docs.docker.com/engine/install/) and [docker compose](https://docs.docker.com/compose/install/) are required to run the project.

Installation steps:
- clone the repository and `cd` to the top-level directory
- create `docker/.env` file and fill it with secrets - for development copy the contents of `docker/.env.example` will suffice (see [notes](#notes-on-envexample) below)
- `docker compose up -d --build` - build and run the containers
- `./scripts/command.sh migrate` - apply migrations
- (optional) `./scripts/command.sh createsuperuser` - create admin user

The **development server** will listen at `localhost:8000` after ensuring that PostgreSQL database is available.

[**Email outbox**](#mailpit) can be checked at `localhost:8025`.

> [!NOTE]
> This setup implements certain security practices like loading secrets from `.env`,
> but **it is not production ready**. Serving the app with nginx and gunicorn 
> would be recommended for production usage.

#### Notes on `.env` and `.env.example`

The project implements secrets management via an `.env` file, utilized by docker orchestration for providing secrets through environment variables.

The values provided in `.env.example` file can be used in `.env` file only for 
development purposes. 

The `API_NINJAS_API_KEY` value in `.env.example` is a valid key, although monthly usage limits may be reached, since it's publicly available through this repo.

### Installation without docker

If non-containerized installation is preferred, at `no-docker` git branch is a project version suited for
direct installation.

Installation steps:
- clone the repository and `cd` to the top-level directory
- `git checkout no-docker` - change branch 
- `python -m venv venv` - create virtual environment
- `source venv/bin/activate` - activate virtual environment
- `pip install -r requirements.txt` - install packages
- `cd refund_request_processing_system`
- `python manage.py migrate` - apply migrations
- (optional) `python manage.py createsuperuser` - create admin user
- (optional) configure environment variables if desired, [as described below](#environment-variables)
- `python manage.py runserver` - run the development server

The **development server** will listen at `localhost:8000`.

With this installation:
- SQLite is used as the database,
- file system cache is used instead of Redis,
- emails are logged to the console.

#### Environment variables

An `.env.example` file is provided to list used environment variables and default values. **None of these variables is suitable for production.**

Below is a full list with comments:

- `SECRET_KEY=insecure-secret-key`
- `DEBUG=1` - should be changed to `0` to test 404 and 500 response handlers
- `DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1`
- `DATABASE_ENGINE=django.db.backends.sqlite3`
- `DATABASE_USER=` - kept for consistency, used for PostgreSQL on branch `master`
- `DATABASE_PASSWORD=` - same
- `DATABASE_HOST=` - same
- `DATABASE_PORT=` - same
- `DATABASE_DB=sqlite3.db`
- `BASE_URL=http://localhost:8000`
- `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`
- `EMAIL_HOST=` - kept for consistency, used for Mailpit on branch `master`
- `EMAIL_PORT=` - same
- `API_NINJAS_API_KEY=4r5s/X/fxaljNyCcrlldlA==jK1lAnTXcbRTDUQS` - a working API key for development purposes
- `CACHE_BACKEND=django.core.cache.backends.filebased.FileBasedCache`
- `REDIS_HOSTNAME=` - kept for consistency, used for Redis cache on branch `master`
- `REDIS_MAIN_DB=` - same


## Account management

Only authenticated users can file refund requests. Account-related URLs:
- `accounts/login/` - logging in
- `accounts/signup/` - creating an account
- `accounts/logout/` - logging out, redirects to the login page
- `accounts/password_reset/` - password reset
- `accounts/password_reset/done/` - confirmation of filing a reset request
- `accounts/reset/<uidb64>/<token>/` - secure password reset link
- `accounts/reset/done/` - password reset confirmation page

Password reset functionality will send an emails with a reset link - the email
can be checked throught Mailpit service at `localhost:8025` or in the development 
server logs in case of direct installation.

## Refund requests UI

Logged in users have to following URLs available:

### `refunds/`

Displays a list of refund requests filed by the logged in user, ordered from the most recent and paginated by 10.

By clicking on each request, users can expand and collaps basic details and are presented with a full details link for the request.

### `refunds/<pk>/`

Displays full details of the given refund request. Only accessible by the user who filed the request. 

Presented data includes:
- request number,
- request status,
- order number and date,
- ordered products,
- request reason,
- address data,
- banking data,
- requestor identity and contant data,
- request creation date.

### `refunds/create/`

Enables user to file a refund request via a form. 

The form is prepopulated with:
- user identity data,
- address and banking information from the previous request of this user, if exists.

The form is validated on the client side, i.e. submission is prevented if data 
is invalid (empty fields or required pattern not matched) - in such case error
messages are displayed next to each invalid field.

Upon submitting the form, user is redirected to his refund requests list.

#### IBAN validation

The IBAN number is validated when the user unfocuses the IBAN or country field, via an API call to the backend (`api/validate-iban/`), which in turn relies on [API Ninjas IBAN validation](https://api-ninjas.com/api/iban). IBAN validation includes:
- checking if a valid number was provided,
- ensuring that the IBAN comes from the same country as provided in the address 'country' field.

After form submission IBAN number is also validated before saving the form.

> [!NOTE]
> Validation results are **cached on the frontend and backend** side, to prevent re-validating same inputs, and to limit usage of external API limits. In both cases **caching includes IBAN-country pairs**.
>
> If prepopulating the form with an already validated IBAN number, it is marked as valid in the results cache, to also prevent re-validation of the same input.

> [!WARNING]
> If the IBAN validation API is unavailable when saving the form after submission,
> it will be still saved, but IBAN will be marked as not validated. The validation can be [re-triggered via admin list action](#triggering-iban-validation).

## Admin site

Admin site allows viewing and and managing refund requests and exporting them as CSV.

### Refund requests list

List includes the following information:
- request id
- status
- iban verification status
- creation date and time
- last update date and time
- order number
- requestor full name
- requestor email
- requestor phone number
- requestor country,
- admin notes preview (50 characters).

The list is sorted by request status (pending, rejected, approved) and request creation date descending (from the newest).

### Refund requests exporting

Exporting to CSV file is possible via `export` button on the list view.

### Refund requests list actions

#### Status change

The admin can change refund request status to `approved`, `rejected` and back to `pending` if desired. 

Changing status to the opposite (between `rejected` and `approved`) is prohibited
to prevent mistakes. Prior change to status `pending` is required.

> [!NOTE]
> Upon refund request status change, a **notification email** with HTML and text version is emitted to each requestor.

#### Triggering IBAN validation

If IBAN validation service would be unavailable when saving the refund request form, IBAN number will be marked as not verified. In such case, admin can trigger re-validation.

### Refund requests details

Full details of each refund request can be viewed. 

Admin site prevents any direct edition of refund requests, to prevent changing the original data provided by users. Instead, a `notes` field is provided for keeping additional information.

This behavior might be changed in the future with e.g. implementation of refund request history in the database.

## Email emission system

A basic email emission system is implemented. 

Emails inheriting from `apps.core.email.BaseEmailMessage` are **stored in the database**. Each email stores an M2M relation to it's recipients and may implement
relations to further objects, on which email context relies (e.g. `RefundRequest` model in case of status change notification email).

Emails are **sent with HTML and text content**, which is provided via **email templates**. Both templates for each email are expected to have the same name and location and differ only with file extension.

This system allows tracking emission date of each email and recreation of its contents via class properties and database relations.

### Mailpit

For development, a [Mailpit](https://mailpit.axllent.org/) container is added. It provides an outbox at `localhost:8025`, which is convenient for **viewing the emitted emails**.

Mailpit is only available with containerized installation.

## Error handling

Custom error pages are provided for the case of 404 and 500 status codes.

## Tests

To run unit tests, use the command `./scripts/command.sh test`.

In case of direct installation, run `python manage.py test` in `refund_request_processing_system` directory.