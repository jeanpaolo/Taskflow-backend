"""
Unit tests for TaskFlow database models.
"""
import pytest
from datetime import datetime
from src.models.user import User, Project, Tag, Task, db


class TestUserModel:
    """Test cases for User model."""
    
    def test_user_creation(self, client):
        """Test creating a new user."""
        with client.application.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.password_hash is not None
            assert user.password_hash != 'password123'  # Should be hashed
    
    def test_password_hashing(self, client):
        """Test password hashing and verification."""
        with client.application.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            
            # Password should be hashed
            assert user.password_hash != 'password123'
            
            # Should verify correct password
            assert user.check_password('password123') is True
            
            # Should reject incorrect password
            assert user.check_password('wrongpassword') is False
    
    def test_user_to_dict(self, client, test_user):
        """Test user serialization to dictionary."""
        with client.application.app_context():
            user = User.query.get(test_user.id)
            user_dict = user.to_dict()
            
            assert 'id' in user_dict
            assert 'username' in user_dict
            assert 'email' in user_dict
            assert 'created_at' in user_dict
            assert 'password_hash' not in user_dict  # Should not expose password
            
            assert user_dict['username'] == 'testuser'
            assert user_dict['email'] == 'test@example.com'
    
    def test_user_repr(self, client, test_user):
        """Test user string representation."""
        with client.application.app_context():
            user = User.query.get(test_user.id)
            assert repr(user) == '<User testuser>'


class TestProjectModel:
    """Test cases for Project model."""
    
    def test_project_creation(self, client, test_user):
        """Test creating a new project."""
        with client.application.app_context():
            user = User.query.get(test_user.id)
            project = Project(
                name='Test Project',
                description='A test project',
                color='#FF5733',
                user_id=user.id
            )
            
            assert project.name == 'Test Project'
            assert project.description == 'A test project'
            assert project.color == '#FF5733'
            assert project.user_id == user.id
    
    def test_project_default_color(self, client, test_user):
        """Test project default color."""
        with client.application.app_context():
            user = User.query.get(test_user.id)
            project = Project(name='Test Project', user_id=user.id)
            assert project.color == '#3B82F6'  # Default color
    
    def test_project_to_dict(self, client, test_project):
        """Test project serialization to dictionary."""
        with client.application.app_context():
            project = Project.query.get(test_project.id)
            project_dict = project.to_dict()
            
            assert 'id' in project_dict
            assert 'name' in project_dict
            assert 'description' in project_dict
            assert 'color' in project_dict
            assert 'user_id' in project_dict
            assert 'created_at' in project_dict
            assert 'task_count' in project_dict
            
            assert project_dict['name'] == 'Test Project'
            assert project_dict['task_count'] == 0  # No tasks initially
    
    def test_project_repr(self, client, test_project):
        """Test project string representation."""
        with client.application.app_context():
            project = Project.query.get(test_project.id)
            assert repr(project) == '<Project Test Project>'


class TestTagModel:
    """Test cases for Tag model."""
    
    def test_tag_creation(self, client, test_user):
        """Test creating a new tag."""
        with client.application.app_context():
            user = User.query.get(test_user.id)
            tag = Tag(
                name='Important',
                color='#FF0000',
                user_id=user.id
            )
            
            assert tag.name == 'Important'
            assert tag.color == '#FF0000'
            assert tag.user_id == user.id
    
    def test_tag_default_color(self, client, test_user):
        """Test tag default color."""
        with client.application.app_context():
            user = User.query.get(test_user.id)
            tag = Tag(name='Test Tag', user_id=user.id)
            assert tag.color == '#6B7280'  # Default color
    
    def test_tag_to_dict(self, client, test_tag):
        """Test tag serialization to dictionary."""
        with client.application.app_context():
            tag = Tag.query.get(test_tag.id)
            tag_dict = tag.to_dict()
            
            assert 'id' in tag_dict
            assert 'name' in tag_dict
            assert 'color' in tag_dict
            assert 'user_id' in tag_dict
            assert 'created_at' in tag_dict
            
            assert tag_dict['name'] == 'Test Tag'
    
    def test_tag_repr(self, client, test_tag):
        """Test tag string representation."""
        with client.application.app_context():
            tag = Tag.query.get(test_tag.id)
            assert repr(tag) == '<Tag Test Tag>'


class TestTaskModel:
    """Test cases for Task model."""
    
    def test_task_creation(self, client, test_user):
        """Test creating a new task."""
        with client.application.app_context():
            user = User.query.get(test_user.id)
            task = Task(
                title='Test Task',
                description='A test task',
                priority=2,
                user_id=user.id
            )
            
            assert task.title == 'Test Task'
            assert task.description == 'A test task'
            assert task.priority == 2
            assert task.completed is False  # Default value
            assert task.user_id == user.id
    
    def test_task_defaults(self, client, test_user):
        """Test task default values."""
        with client.application.app_context():
            user = User.query.get(test_user.id)
            task = Task(title='Test Task', user_id=user.id)
            
            assert task.completed is False
            assert task.priority == 1  # Default priority
            assert task.due_date is None
            assert task.project_id is None
    
    def test_task_with_project_and_tags(self, client, test_task):
        """Test task with project and tags relationships."""
        with client.application.app_context():
            task = Task.query.get(test_task.id)
            assert task.project is not None
            assert task.project.name == 'Test Project'
            assert len(task.tags) == 1
            assert task.tags[0].name == 'Test Tag'
    
    def test_task_to_dict(self, client, test_task):
        """Test task serialization to dictionary."""
        with client.application.app_context():
            task = Task.query.get(test_task.id)
            task_dict = task.to_dict()
            
            required_fields = [
                'id', 'title', 'description', 'completed', 'priority',
                'due_date', 'project_id', 'project', 'user_id', 'tags',
                'created_at', 'updated_at'
            ]
            
            for field in required_fields:
                assert field in task_dict
            
            assert task_dict['title'] == 'Test Task'
            assert task_dict['completed'] is False
            assert task_dict['priority'] == 2
            assert task_dict['project']['name'] == 'Test Project'
            assert len(task_dict['tags']) == 1
            assert task_dict['tags'][0]['name'] == 'Test Tag'
    
    def test_task_repr(self, client, test_task):
        """Test task string representation."""
        with client.application.app_context():
            task = Task.query.get(test_task.id)
            assert repr(task) == '<Task Test Task>'


class TestModelRelationships:
    """Test cases for model relationships."""
    
    def test_user_projects_relationship(self, client, test_user, test_project):
        """Test user-projects relationship."""
        with client.application.app_context():
            user = User.query.get(test_user.id)
            project = Project.query.get(test_project.id)
            assert project in user.projects
            assert project.user == user
    
    def test_user_tags_relationship(self, client, test_user, test_tag):
        """Test user-tags relationship."""
        with client.application.app_context():
            user = User.query.get(test_user.id)
            tag = Tag.query.get(test_tag.id)
            assert tag in user.tags
            assert tag.user == user
    
    def test_user_tasks_relationship(self, client, test_user, test_task):
        """Test user-tasks relationship."""
        with client.application.app_context():
            user = User.query.get(test_user.id)
            task = Task.query.get(test_task.id)
            assert task in user.tasks
            assert task.user == user
    
    def test_project_tasks_relationship(self, client, test_project, test_task):
        """Test project-tasks relationship."""
        with client.application.app_context():
            project = Project.query.get(test_project.id)
            task = Task.query.get(test_task.id)
            assert task in project.tasks
            assert task.project == project
    
    def test_task_tags_many_to_many(self, client, test_task, test_tag):
        """Test task-tags many-to-many relationship."""
        with client.application.app_context():
            task = Task.query.get(test_task.id)
            tag = Tag.query.get(test_tag.id)
            assert tag in task.tags
            assert task in tag.tasks
    
    def test_cascade_delete_user(self, client, test_user):
        """Test cascade delete when user is deleted."""
        with client.application.app_context():
            user = User.query.get(test_user.id)
            user_id = user.id
            
            # Create related objects
            project = Project(name='Test Project', user_id=user_id)
            tag = Tag(name='Test Tag', user_id=user_id)
            task = Task(title='Test Task', user_id=user_id)
            
            db.session.add_all([project, tag, task])
            db.session.commit()
            
            # Delete user
            db.session.delete(user)
            db.session.commit()
            
            # Related objects should be deleted
            assert Project.query.filter_by(user_id=user_id).count() == 0
            assert Tag.query.filter_by(user_id=user_id).count() == 0
            assert Task.query.filter_by(user_id=user_id).count() == 0

