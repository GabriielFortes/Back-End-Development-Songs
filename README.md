# 🎵 Songs API – Project with Flask, MongoDB, and Automated Testing

This project was developed as part of the **IBM Back-End Development** course on Coursera.

It is a RESTful API for music management, built with **Flask**, connected to **MongoDB**, and equipped with automated tests using `pytest`.

---

## 🚀 API Features

- ✅ List all songs (`/songs`)
- ✅ Retrieve song by ID (`/song/id`)
- ✅ Create song with duplicate checking (`/song`)
- ✅ Update existing song with change detection (`/song/id`)
- ✅ Delete song by ID (`/song/id`)
- ✅ Count total songs (`/count`)
- ✅ Health check endpoint (`/health`)

---

## 🐳 Running the Project with Docker Compose

No manual setup or environment variables needed!

### Prerequisite

- Docker and Docker Compose installed on your machine.

### Steps

1. Clone the repository:

```bash
git clone https://github.com/GabriielFortes/Back-End-Development-Songs.git
cd Back-End-Development-Songs
```

2. Run the entire stack with:
```bash
docker compose up
```
This command will build and start the backend Flask API, MongoDB, and Mongo Express for database management.

🧪 Automated Tests
The project includes a full test suite with pytest, located in the tests/ directory, covering:

API routes (test_api.py)

Reusable fixtures (conftest.py)

Isolated test environment using test_client

📁 Project Structure
Back-End-Development-Songs/
├── app.py # Main Flask application
├── backend/
│ ├── init.py # Flask app instance
│ └── data/
│ ├── songs.json # Initial data source
│ └── routes.py # API route definitions
├── bin/
│ └── setup.sh # Environment setup script (optional)
├── tests/
│ ├── init.py
│ ├── conftest.py # Pytest fixtures
│ └── test_api.py # API test cases
├── requirements.txt
├── pytest.ini
├── .gitignore
├── LICENSE
└── README.md

▶️ Running Tests inside the backend container
After starting the containers, open a terminal inside the backend container:

```bash
docker exec -it api_concerts_songs sh
```

Then run:
```bash
pytest
```

🤝 Credits
This project was developed as a final project for the IBM Backend Development Capstone Project course:
https://www.coursera.org/professional-certificates/ibm-backend-development

All implementations, modular architecture, tests, and MongoDB integration were completed by me based on the course foundations and further customization.