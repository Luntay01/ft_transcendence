# ft_transcendence

This project is a multiplayer Pong game featuring real-time gameplay, AI opponents, 3D rendering using Three.js, live chat, and more. It is being developed using Django for the backend and Bootstrap for the frontend.

## Project Structure

project/
│
├── backend/                            # Django Backend
│   ├── pong/                           # Main Django app (handles game logic, user management, etc.)
│   ├── users/                          # Django app for user management (registration, authentication, etc.)
│   ├── game/                           # Game logic (API for frontend, game matchmaking)
│   ├── chat/                           # Live chat application
│   ├── api/                            # API app for external/CLI communication
│   ├── Dockerfile                      # Dockerfile for Django backend
│   ├── requirements.txt                # Python dependencies (Django, Redis, Celery, etc.)
│   ├── settings.py                     # Django settings (integrates Redis, PostgreSQL, etc.)
│   ├── celery.py                       # Celery configuration for task handling
│   └── manage.py                       # Django management commands
│
├── frontend/                           # Frontend (JavaScript/Bootstrap/Three.js)
│   ├── src/                            # Source files for the frontend
│   │   ├── assets/                     # Static files (CSS, images, etc.)
│   │   ├── js/                         # JavaScript files (Three.js for 3D rendering, WebSocket logic)
│   │   │   └── game3D.js               # Three.js logic for 3D Pong game
│   │   └── index.html                  # Main HTML file for the UI
│   ├── Dockerfile                      # Dockerfile for the frontend
│   └── package.json                    # Frontend dependencies (Bootstrap, WebSocket libraries, Three.js)
│
├── redis/                              # Redis container setup
│   └── redis.conf                      # Redis configuration file (optional customization)
│   └── Dockerfile                      # Redis container (prebuilt Redis image)
│
├── postgres/                           # PostgreSQL container setup
│   └── init.sql                        # SQL initialization script (for database structure, users, game history)
│   └── Dockerfile                      # PostgreSQL container (prebuilt Postgres image)
│
├── ai/                                 # AI Logic
│   └── ai_worker.py                    # AI logic processing file (Celery task for asynchronous AI processing)
│   └── Dockerfile                      # Dockerfile for AI processing
│
├── websocket/                          # WebSocket server for real-time game and chat
│   └── ws_server.py                    # WebSocket server logic for real-time game updates and chat
│   └── Dockerfile                      # Dockerfile for WebSocket service
│
├── cli_game/                           # CLI Pong Game setup
│   └── cli_pong.py                     # Main Python file for CLI Pong game logic
│   └── Dockerfile                      # Dockerfile for CLI Pong
│
├── nginx/                              # Nginx reverse proxy (optional)
│   └── nginx.conf                      # Nginx configuration for routing requests to different services
│   └── Dockerfile                      # Dockerfile for Nginx
│
├── docker-compose.yml                  # Docker Compose file to orchestrate all containers
├── .env                                # Environment variables for sensitive data (PostgreSQL, Redis settings)


## Technologies Used

- **Django** for the backend
- **PostgreSQL** for the database
- **Redis** for caching and task queue management
- **Three.js** for 3D rendering of the Pong game
- **WebSocket** for real-time game updates and live chat
- **Celery** for handling AI logic in the background
- **Docker** for containerization

## Project Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/ft_transcendence.git
   cd ft_transcendence/project

1. Build the Docker containers:
   docker-compose up --build

2. Add environment variables to the .env file
   DJANGO_SECRET_KEY=your_secret_key
   POSTGRES_DB=pongdb
   POSTGRES_USER=ponguser
   POSTGRES_PASSWORD=your_password