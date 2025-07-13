"""
Pytest configuration and shared fixtures for TaskFlow backend tests.
"""
import pytest
import tempfile
import os
from src.main import app
from src.models.user import db, User, Project, Tag, Task
from flask_jwt_extended import create_access_token


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    # Create a temporary database file
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{app.config["DATABASE"]}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


@pytest.fixture
def test_user(client):
    """Create a test user in the database."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        
        # Refresh the user to ensure it's attached to the session
        user = User.query.filter_by(username='testuser').first()
        return user


@pytest.fixture
def auth_headers(client, test_user):
    """Create authentication headers with JWT token."""
    with app.app_context():
        # Get fresh user from database to ensure session attachment
        user = User.query.get(test_user.id)
        token = create_access_token(identity=str(user.id))
        return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def test_project(client, test_user):
    """Create a test project."""
    with app.app_context():
        # Get fresh user from database
        user = User.query.get(test_user.id)
        project = Project(
            name='Test Project',
            description='A test project',
            color='#3B82F6',
            user_id=user.id
        )
        db.session.add(project)
        db.session.commit()
        
        # Return fresh project from database
        project = Project.query.filter_by(name='Test Project').first()
        return project


@pytest.fixture
def test_tag(client, test_user):
    """Create a test tag."""
    with app.app_context():
        # Get fresh user from database
        user = User.query.get(test_user.id)
        tag = Tag(
            name='Test Tag',
            color='#10B981',
            user_id=user.id
        )
        db.session.add(tag)
        db.session.commit()
        
        # Return fresh tag from database
        tag = Tag.query.filter_by(name='Test Tag').first()
        return tag


@pytest.fixture
def test_task(client, test_user, test_project, test_tag):
    """Create a test task with project and tag."""
    with app.app_context():
        # Get fresh objects from database
        user = User.query.get(test_user.id)
        project = Project.query.get(test_project.id)
        tag = Tag.query.get(test_tag.id)
        
        task = Task(
            title='Test Task',
            description='A test task',
            priority=2,
            user_id=user.id,
            project_id=project.id
        )
        task.tags.append(tag)
        db.session.add(task)
        db.session.commit()
        
        # Return fresh task from database
        task = Task.query.filter_by(title='Test Task').first()
        return task


@pytest.fixture
def multiple_users(client):
    """Create multiple test users."""
    with app.app_context():
        users = []
        for i in range(3):
            user = User(
                username=f'user{i}',
                email=f'user{i}@example.com'
            )
            user.set_password('password123')
            db.session.add(user)
        db.session.commit()
        
        # Return fresh users from database
        for i in range(3):
            user = User.query.filter_by(username=f'user{i}').first()
            users.append(user)
        return users


@pytest.fixture
def sample_data(client, test_user):
    """Create sample data for comprehensive testing."""
    with app.app_context():
        # Get fresh user from database
        user = User.query.get(test_user.id)
        
        # Create projects
        projects = []
        for i in range(3):
            project = Project(
                name=f'Project {i}',
                description=f'Description for project {i}',
                color=f'#{"123456"[i:i+6].ljust(6, "0")}',
                user_id=user.id
            )
            db.session.add(project)
            projects.append(project)
        
        # Create tags
        tags = []
        for i in range(3):
            tag = Tag(
                name=f'Tag {i}',
                color=f'#{"ABCDEF"[i:i+6].ljust(6, "0")}',
                user_id=user.id
            )
            db.session.add(tag)
            tags.append(tag)
        
        db.session.commit()
        
        # Get fresh objects from database
        projects = [Project.query.filter_by(name=f'Project {i}').first() for i in range(3)]
        tags = [Tag.query.filter_by(name=f'Tag {i}').first() for i in range(3)]
        
        # Create tasks
        tasks = []
        for i in range(5):
            task = Task(
                title=f'Task {i}',
                description=f'Description for task {i}',
                priority=(i % 3) + 1,
                completed=i % 2 == 0,
                user_id=user.id,
                project_id=projects[i % len(projects)].id
            )
            # Add random tags
            task.tags.append(tags[i % len(tags)])
            db.session.add(task)
            tasks.append(task)
        
        db.session.commit()
        
        # Get fresh tasks from database
        tasks = [Task.query.filter_by(title=f'Task {i}').first() for i in range(5)]
        
        return {
            'user': user,
            'projects': projects,
            'tags': tags,
            'tasks': tasks
        }

