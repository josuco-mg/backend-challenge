## Author

Jose Antonio Martin

## Introduction

This project contains a dockerized application that implements a REST API for managing ECGs.

The stack is based on Python/Django, PostgreSQL for the database, and Celery for running background tasks (with Redis as broker).

The architecture tries to follow Domain Driven Design principles, and the code is fully tested.

## Requirements

You need Docker and Docker Compose installed in your system.

You will also need some kind of API testing tool (I recommend [HTTPie](https://httpie.io/)).

## Quick start

There is a makefile with some useful commands, but you'll probably only need the following:

- `make up`: runs the whole stack.
- `make test`: runs the test suite.

## API

The functionality exposed by the API is limited to the following:

- Obtain a JWT token for authentication, providing a username and password.
- Create a new user.
- Create a new ECG.
- Obtain the stats for a given ECG.

Some endpoints require authentication. In those cases, a valid JWT token must be provided in the `Authorization` header (`Bearer` scheme).

An initial admin user is created on startup, with username `admin` and password `admin`.

The API exposes the following endpoints, available locally on `localhost:5005`:

- `POST /api/token/`: obtains a JWT token for authentication.
  - Requires authentication: no.
  - Payload:
    ```json
    {
      "username": string,
      "password": string
    }
    ```
  - Returns:
    ```json
    {
      "access": string,
      "refresh": string
    }
    ```
  - HTTPie example: `http POST localhost:5005/api/token/ username=admin password=admin`

- `POST /api/users/`: creates a new user.
  - Requires authentication: yes (limited to admin users).
  - Payload:
    ```json
    {
      "username": string,
      "password": string,
      "is_admin": boolean (optional)
    }
    ```
  - Returns:
    ```json
    {
      "id": integer,
    }
    ```
  - HTTPie example: `http POST localhost:5005/api/users/ username=creator password=creator authorization:"Bearer <token>"`

- `POST /api/ecgs/`: creates a new ECG.
  - Requires authentication: yes (limited to regular users).
  - Payload:
    ```json
    {
      "lead_results": [
        {
          "lead": string,
          "signal": [integer, ...],
          "num_samples": integer (optional)
        },
        ...
      ]
    }
    ```
  - Returns:
    ```json
    {
      "id": 0,
    }
    ```
  - HTTPie example: `http POST localhost:5005/api/ecgs/ lead_results:='[{"lead": "I", "signal": [1, -1, 1, -1]}, {"lead": "II", "signal": [1, 1, 1, 1]}]' authorization:"Bearer <token>"`

- `GET /api/ecgs/{id}/stats/`: returns the stats for the given ECG.
  - Requires authentication: yes (limited to the owner of the ECG).
  - Returns:
    ```json
    {
      "lead_results": [
        {
          "lead": string,
          "zero_crossing_count": integer
        },
        ...
      ]
    }
    ```
  - HTTPie example: `http GET localhost:5005/api/ecgs/{id}/stats/ authorization:"Bearer <token>"`

## Architecture

There are three main components:

- The account module: contains the high level User domain model, a repository adapter to abstract the persistence layer, and required user services/use cases.
- The ecg module: same as the account module, but for the ECG/ECGLeadResult domain models.
- The Django application, that implements the API and the concrete persistence layer (against PostgreSQL).

The aim is achieving dependency inversion, so that the domain is not coupled to the persistence layer or the API.

I used a unit of work pattern too, to abstract the concept of atomic operations away from the services.
