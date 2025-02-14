# My Project

This project is a web application that consists of a Django backend and a Svelte frontend, containerized separately using Docker.

## Project Structure

```
my-project
├── backend
│   ├── manage.py
│   ├── myproject
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── app
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend
│   ├── public
│   │   └── index.html
│   ├── src
│   │   ├── App.svelte
│   │   └── main.js
│   ├── Dockerfile
│   └── package.json
└── README.md
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose (optional, for easier management)

### Backend Setup

1. Navigate to the `backend` directory.
2. Build the Docker image:
   ```
   docker build -t my-django-backend .
   ```
3. Run the Docker container:
   ```
   docker run -p 8000:8000 my-django-backend
   ```
4. Access the backend at `http://localhost:8000`.

### Frontend Setup

1. Navigate to the `frontend` directory.
2. Build the Docker image:
   ```
   docker build -t my-svelte-frontend .
   ```
3. Run the Docker container:
   ```
   docker run -p 5000:5000 my-svelte-frontend
   ```
4. Access the frontend at `http://localhost:5000`.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.

## License

This project is licensed under the MIT License.