# Social Network Project

A Twitter-like social network web application built with Django.

## Features

- **User Authentication**: Register, login, and logout.
- **Posts**: Create posts with text and images.
- **Likes**: Like/unlike posts and comments.
- **Comments**: Comment on posts.
- **Profile**: View user profiles with their posts.
- **Following**: Follow/unfollow users (data model support, frontend integration may vary).
- **Search**: Search posts by content or tags (uses stemming and trigrams).
- **Tags**: specific tags filtering.
- **Pagination**: Posts are paginated.

## Prerequisites

- Python 3.8+
- pip

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd project4
    ```

2.  **Create and activate a virtual environment (optional but recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations:**
    ```bash
    python3 manage.py makemigrations
    python3 manage.py migrate
    ```

5.  **Create a superuser (optional, for admin access):**
    ```bash
    python3 manage.py createsuperuser
    ```

## Running the Application

1.  **Start the development server:**
    ```bash
    python3 manage.py runserver
    ```

2.  **Access the application:**
    Open your web browser and go to `http://127.0.0.1:8000/`.

## NLTK Data

The search functionality uses NLTK for stemming. If you encounter errors related to missing NLTK resources, you may need to download them:

```python
import nltk
nltk.download('punkt')
nltk.download('wordnet')
```
(Usually `porter_stemmer` works without extra downloads, but `punkt` might be needed depending on internal usage).

## API Endpoints

- `/`: Home page (all posts)
- `/login`: Login page
- `/register`: Registration page
- `/create_post/`: Page to create a new post
- `/profile/<id>/`: User profile page
- `/search/`: Search results
