

# **Django To-Do Management API**

A **Django REST Framework**-based project to manage tasks and projects with role-based access control, authentication using JWT, and advanced features like time-based access restrictions and task approval workflows.

---

## **Features**

### 1. **Task Management**
- Create, retrieve, update, and delete tasks.
- Role-based restrictions on task operations:
  - **Admin**: Full access to all tasks.
  - **Manager**: Can create and update tasks, and mark them as completed.
  - **User**: Can create, view, edit, and delete only assigned tasks.
- Support for task statuses such as `Pending`, `In Progress`, `Completed`, and `Pending Approval`.
- Filtering and sorting by priority, status, and due date.

### 2. **Project Management**
- Create, retrieve, update, and delete projects.
- Automatically display a summary of tasks under each project.
- Admin-only permission to delete projects and related tasks.

### 3. **Authentication**
- **User Registration**: Supports email verification.
- **JWT Authentication**:
  - Login endpoint to obtain `access` and `refresh` tokens.
  - Logout endpoint to invalidate tokens using a blocklist.
  - Time-restricted access control for JWT tokens.

### 4. **Authorization**
- Role-based permissions with three roles: `Admin`, `Manager`, and `User`.

### 5. **Task Approval Workflow**
- Managers can approve or revoke tasks with the `Pending Approval` status.

### 6. **Time-Based Access**
- Restrict user access to tasks based on allowed time slots:
  - **Users**: Access only allowed between 3:00 PM and 11:59 PM.

### 7. **Delayed Task Saving with Redis**
- Pending tasks are saved temporarily in Redis and only moved to the main database upon manager approval.

---

## **API Endpoints**

### **Task Management**
| Endpoint                             | Method | Description                                    |
|--------------------------------------|--------|------------------------------------------------|
| `/tasks/`                            | GET    | Retrieve a list of all tasks (with filters).   |
| `/create/`                           | POST   | Create a new task.                             |
| `/tasks/<int:pk>/`                   | PUT    | Update a task.                                 |
| `/tasks/<int:pk>/delete/`            | DELETE | Delete a task (role-based restrictions apply). |
| `/approve/<int:task_id>/`            | POST   | Approve a pending task.                        |
| `/revoke/<int:task_id>/`             | POST   | Revoke approval for a pending task.            |
| `/tasks/pending/`                    | GET    | Retrieve a list of pending tasks.              |

### **Project Management**
| Endpoint                             | Method | Description                                    |
|--------------------------------------|--------|------------------------------------------------|
| `/projects/<int:pk>/`                | GET    | Retrieve details of a specific project.        |
| `/projects/<int:pk>/delete/`         | DELETE | Delete a project (Admin-only).                |
| `/projects/create/`                  | POST   | Create a new project.                          |
| `/projects/<int:pk>/update/`         | PUT    | Update an existing project.                    |

### **Authentication**
| Endpoint                             | Method | Description                                    |
|--------------------------------------|--------|------------------------------------------------|
| `/register/`                         | POST   | Register a new user with email verification.   |
| `/login/`                            | POST   | Login and obtain JWT tokens.                   |
| `/token/refresh/`                    | POST   | Refresh JWT tokens.                            |
| `/logout/`                           | POST   | Logout and invalidate tokens.                  |
| `/activate/<uidb64>/<token>/`        | GET    | Activate user accounts via email verification. |

---

## **Project Structure**

```
main/
├── account/
│   ├── models.py        # UserProfile model for role-based authentication.
│   ├── serializers.py   # Serializers for registration and authentication.
│   ├── views.py         # Registration, login, and logout APIs.
│   └── urls.py          # Routes for authentication APIs.
├── base/
│   ├── models.py        # Models for Task and Project.
│   ├── serializers.py   # Serializers for Task and Project.
│   ├── views.py         # CRUD operations and approval workflows.
│   └── urls.py          # Routes for task and project APIs.
├── main/
│   ├── settings.py      # Project settings (includes Celery, Redis configs).
│   ├── urls.py          # Main URL configuration.
│   └── celery.py        # Celery setup for task queue management.
├── templates/           # Optional templates for API testing.
├── README.md            # Documentation file.
└── manage.py            # Django management script.
```

---



### **Steps**

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd main
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

     ```

5. Run Redis server:
   ```bash
   redis-server
   ```

6. Start Celery workers and beat scheduler:
   ```bash
   celery -A main worker --loglevel=info
   celery -A main beat --loglevel=info
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

---

## **Usage**

1. **Register and Activate User**:
   - Register a user via `/register/`.
   - Activate the account using the email link.

2. **Login and Obtain Tokens**:
   - Use `/login/` to get `access` and `refresh` tokens.
   - Use tokens for authentication in Postman.

3. **Manage Tasks and Projects**:
   - Perform CRUD operations using the task and project endpoints.

---

## **Testing**

### **Postman**
- Use Postman to test the endpoints.
- Add the `Authorization` header for protected endpoints:
  ```
  Authorization: Bearer <ACCESS_TOKEN>
  ```

## **License**

This project is licensed under the MIT License.
