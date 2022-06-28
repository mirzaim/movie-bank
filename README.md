# Flask Movie API

This project is a Python web service implemented using Flask, with routes to manage movies, users, votes, and comments. It also uses JWT for authentication and MongoDB as the database.

## Project Structure

```
.
├── Dockerfile
├── app
│   └── app.py            # Main Flask application
├── docker-compose.yml    # Docker Compose setup
├── requirements.txt
└── swagger.yaml 
```

## Getting Started

### Installation

1. **Clone the repository:**

   ```
   git clone https://github.com/mirzaim/movie-bank.git
   cd movie-bank
   ```

2. **Install dependencies:**

   If you prefer to run the app locally without Docker, first install the dependencies:

   ```
   pip install -r requirements.txt
   ```

### Running the Application with Docker

1. **Build the Docker image:**

   ```
   docker-compose build
   ```

2. **Run the application:**

   ```
   docker-compose up
   ```

   This will start the Flask application.

3. **Access the API:**

   Once the application is running, you can access the API at:

   ```
   http://localhost:5000/
   ```

   This will return a test response, including a list of users, movies, and comments.

### Running the Application Locally (Without Docker)

1. **Run the Flask application:**

   If you prefer running the app locally without Docker, you can directly run it with Python:

   ```
   python app/app.py
   ```

2. **Access the API:**

   You can access the API at `http://localhost:5000/`.

### API Endpoints

Here is a brief summary of available API endpoints:

- **GET /**: Returns a test response with all users, movies, and comments.
- **POST /login**: Login to get a JWT token.
- **GET /protected**: Access a protected route (requires JWT token).
- **POST /admin/movie**: Add a new movie (admin-only).
- **PUT /admin/movie/<int:movie_id>**: Update a movie (admin-only).
- **DELETE /admin/movie/<int:movie_id>**: Delete a movie (admin-only).
- **POST /user/vote**: Add a vote for a movie (user-only).
- **POST /user/comment**: Add a comment on a movie (user-only).
- **GET /comments**: Get approved comments for a movie.
- **GET /movies**: Get the list of movies.
- **GET /movie/<int:movie_id>**: Get details of a specific movie.
