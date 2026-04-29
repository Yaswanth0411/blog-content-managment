# 📝 Blog Content Management System (Django)

## 📌 Overview
This project is a **Blog Content Management System** built using the Django framework. It allows users to create, view, update, and delete blog posts through a simple and structured interface.

The application follows Django’s **MVT (Model-View-Template)** architecture and uses Django ORM for database operations.

---

## 🚀 Features
- Create new blog posts
- View all blog posts
- Edit existing posts
- Delete posts
- Timestamp for blog entries
- Dynamic content rendering using templates

---

## 🛠️ Tech Stack

| Layer        | Technology |
|-------------|-----------|
| Backend     | Django (Python) |
| Database    | SQLite (default Django DB) |
| Frontend    | HTML, CSS |
| ORM         | Django ORM |

---

## 🧱 Project Structure
blog_project/
│
├── blog/
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│ ├── templates/
│ │ ├── index.html
│ │ ├── create.html
│ │ ├── edit.html
│
├── blog_project/
│ ├── settings.py
│ ├── urls.py
│
├── db.sqlite3
├── manage.py


---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Yaswanth0411/blog-content-managment.git
cd blog-content-managment

### Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

### Install Dependencies
pip install django

### Migrate the files
python manage.py migrate

### Run the server
python manage.py runserver

### Open in Browser
http://127.0.0.1:8000/