"""
Unit tests for task routes.
"""
import pytest
import json
from datetime import datetime, timedelta
from src.models.user import Task, Tag, db


class TestTaskRoutes:
    """Test cases for task endpoints."""
    
    def test_get_tasks_empty(self, client, auth_headers):
        """Test getting tasks when user has none."""
        response = client.get('/api/tasks', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'tasks' in response_data
        assert response_data['tasks'] == []
    
    def test_get_tasks_with_data(self, client, auth_headers, test_task):
        """Test getting tasks when user has tasks."""
        response = client.get('/api/tasks', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'tasks' in response_data
        assert len(response_data['tasks']) == 1
        assert response_data['tasks'][0]['title'] == 'Test Task'
        assert response_data['tasks'][0]['description'] == 'A test task'
        assert response_data['tasks'][0]['priority'] == 2
        assert response_data['tasks'][0]['completed'] is False
    
    def test_get_tasks_unauthorized(self, client):
        """Test getting tasks without authentication."""
        response = client.get('/api/tasks')
        assert response.status_code == 401
    
    def test_create_task_success(self, client, auth_headers):
        """Test successful task creation."""
        data = {
            'title': 'New Task',
            'description': 'A new task description',
            'priority': 3
        }
        
        response = client.post('/api/tasks',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        
        assert 'message' in response_data
        assert 'task' in response_data
        assert response_data['task']['title'] == 'New Task'
        assert response_data['task']['description'] == 'A new task description'
        assert response_data['task']['priority'] == 3
        assert response_data['task']['completed'] is False
    
    def test_create_task_minimal_data(self, client, auth_headers):
        """Test creating task with minimal required data."""
        data = {'title': 'Minimal Task'}
        
        response = client.post('/api/tasks',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        
        assert response_data['task']['title'] == 'Minimal Task'
        assert response_data['task']['description'] == ''  # Default empty
        assert response_data['task']['priority'] == 1  # Default priority
        assert response_data['task']['completed'] is False
    
    def test_create_task_missing_title(self, client, auth_headers):
        """Test creating task without required title field."""
        data = {'description': 'Task without title'}
        
        response = client.post('/api/tasks',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Title is required' in response_data['error']
    
    def test_create_task_with_project(self, client, auth_headers, test_project):
        """Test creating task with project assignment."""
        data = {
            'title': 'Project Task',
            'project_id': test_project.id
        }
        
        response = client.post('/api/tasks',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        
        assert response_data['task']['project_id'] == test_project.id
        assert response_data['task']['project']['name'] == 'Test Project'
    
    def test_create_task_with_tags(self, client, auth_headers, test_tag):
        """Test creating task with tags."""
        data = {
            'title': 'Tagged Task',
            'tags': ['Test Tag', 'New Tag']
        }
        
        response = client.post('/api/tasks',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        
        assert len(response_data['task']['tags']) == 2
        tag_names = [tag['name'] for tag in response_data['task']['tags']]
        assert 'Test Tag' in tag_names
        assert 'New Tag' in tag_names
    
    def test_create_task_with_due_date(self, client, auth_headers):
        """Test creating task with due date."""
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        data = {
            'title': 'Task with Due Date',
            'due_date': due_date
        }
        
        response = client.post('/api/tasks',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        
        assert response_data['task']['due_date'] is not None
    
    def test_create_task_unauthorized(self, client):
        """Test creating task without authentication."""
        data = {'title': 'Unauthorized Task'}
        
        response = client.post('/api/tasks',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 401
    
    def test_get_single_task_success(self, client, auth_headers, test_task):
        """Test getting a single task by ID."""
        response = client.get(f'/api/tasks/{test_task.id}', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'task' in response_data
        assert response_data['task']['id'] == test_task.id
        assert response_data['task']['title'] == 'Test Task'
    
    def test_get_single_task_not_found(self, client, auth_headers):
        """Test getting a non-existent task."""
        response = client.get('/api/tasks/999', headers=auth_headers)
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'Task not found' in response_data['error']
    
    def test_get_single_task_unauthorized(self, client, test_task):
        """Test getting a task without authentication."""
        response = client.get(f'/api/tasks/{test_task.id}')
        assert response.status_code == 401
    
    def test_update_task_success(self, client, auth_headers, test_task):
        """Test successful task update."""
        data = {
            'title': 'Updated Task',
            'description': 'Updated description',
            'priority': 3,
            'completed': True
        }
        
        response = client.put(f'/api/tasks/{test_task.id}',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'message' in response_data
        assert 'task' in response_data
        assert response_data['task']['title'] == 'Updated Task'
        assert response_data['task']['description'] == 'Updated description'
        assert response_data['task']['priority'] == 3
        assert response_data['task']['completed'] is True
    
    def test_update_task_partial(self, client, auth_headers, test_task):
        """Test partial task update."""
        data = {'completed': True}
        
        response = client.put(f'/api/tasks/{test_task.id}',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert response_data['task']['completed'] is True
        # Other fields should remain unchanged
        assert response_data['task']['title'] == 'Test Task'
        assert response_data['task']['priority'] == 2
    
    def test_update_task_tags(self, client, auth_headers, test_task, test_user):
        """Test updating task tags."""
        with client.application.app_context():
            # Create additional tag
            new_tag = Tag(name='Updated Tag', user_id=test_user.id)
            db.session.add(new_tag)
            db.session.commit()
            
            data = {'tags': ['Updated Tag', 'Another Tag']}
            
            response = client.put(f'/api/tasks/{test_task.id}',
                                data=json.dumps(data),
                                content_type='application/json',
                                headers=auth_headers)
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            
            assert len(response_data['task']['tags']) == 2
            tag_names = [tag['name'] for tag in response_data['task']['tags']]
            assert 'Updated Tag' in tag_names
            assert 'Another Tag' in tag_names
    
    def test_update_task_not_found(self, client, auth_headers):
        """Test updating a non-existent task."""
        data = {'title': 'Updated Task'}
        
        response = client.put('/api/tasks/999',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'Task not found' in response_data['error']
    
    def test_update_task_unauthorized(self, client, test_task):
        """Test updating a task without authentication."""
        data = {'title': 'Unauthorized Update'}
        
        response = client.put(f'/api/tasks/{test_task.id}',
                            data=json.dumps(data),
                            content_type='application/json')
        
        assert response.status_code == 401
    
    def test_delete_task_success(self, client, auth_headers, test_task):
        """Test successful task deletion."""
        task_id = test_task.id
        
        response = client.delete(f'/api/tasks/{task_id}', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'Task deleted successfully' in response_data['message']
        
        # Verify task is actually deleted
        with client.application.app_context():
            deleted_task = Task.query.get(task_id)
            assert deleted_task is None
    
    def test_delete_task_not_found(self, client, auth_headers):
        """Test deleting a non-existent task."""
        response = client.delete('/api/tasks/999', headers=auth_headers)
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'Task not found' in response_data['error']
    
    def test_delete_task_unauthorized(self, client, test_task):
        """Test deleting a task without authentication."""
        response = client.delete(f'/api/tasks/{test_task.id}')
        assert response.status_code == 401
    
    def test_task_filtering_by_project(self, client, auth_headers, sample_data):
        """Test filtering tasks by project."""
        project_id = sample_data['projects'][0].id
        
        response = client.get(f'/api/tasks?project_id={project_id}', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        # Should only return tasks from the specified project
        for task in response_data['tasks']:
            assert task['project_id'] == project_id
    
    def test_task_filtering_by_completed(self, client, auth_headers, sample_data):
        """Test filtering tasks by completion status."""
        response = client.get('/api/tasks?completed=true', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        # Should only return completed tasks
        for task in response_data['tasks']:
            assert task['completed'] is True
    
    def test_task_filtering_by_priority(self, client, auth_headers, sample_data):
        """Test filtering tasks by priority."""
        response = client.get('/api/tasks?priority=3', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        # Should only return high priority tasks
        for task in response_data['tasks']:
            assert task['priority'] == 3
    
    def test_task_filtering_by_tag(self, client, auth_headers, sample_data):
        """Test filtering tasks by tag."""
        tag_id = sample_data['tags'][0].id
        
        response = client.get(f'/api/tasks?tag_id={tag_id}', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        # Should only return tasks with the specified tag
        for task in response_data['tasks']:
            tag_ids = [tag['id'] for tag in task['tags']]
            assert tag_id in tag_ids
    
    def test_tasks_user_isolation(self, client, multiple_users):
        """Test that users can only access their own tasks."""
        with client.application.app_context():
            # Create tasks for different users
            user1, user2, user3 = multiple_users
            
            task1 = Task(title='User1 Task', user_id=user1.id)
            task2 = Task(title='User2 Task', user_id=user2.id)
            
            db.session.add_all([task1, task2])
            db.session.commit()
            
            # Create tokens for each user
            from flask_jwt_extended import create_access_token
            token1 = create_access_token(identity=str(user1.id))
            token2 = create_access_token(identity=str(user2.id))
            
            headers1 = {'Authorization': f'Bearer {token1}'}
            headers2 = {'Authorization': f'Bearer {token2}'}
            
            # User1 should only see their task
            response = client.get('/api/tasks', headers=headers1)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['tasks']) == 1
            assert data['tasks'][0]['title'] == 'User1 Task'
            
            # User2 should only see their task
            response = client.get('/api/tasks', headers=headers2)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['tasks']) == 1
            assert data['tasks'][0]['title'] == 'User2 Task'
            
            # User1 should not be able to access User2's task
            response = client.get(f'/api/tasks/{task2.id}', headers=headers1)
            assert response.status_code == 404


class TestTaskNLPRoutes:
    """Test cases for task NLP parsing endpoints."""
    
    def test_parse_task_simple(self, client, auth_headers):
        """Test parsing simple task text."""
        data = {'text': 'Buy groceries'}
        
        response = client.post('/api/tasks/parse',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'parsed' in response_data
        assert response_data['parsed']['title'] == 'Buy groceries'
    
    def test_parse_task_with_priority(self, client, auth_headers):
        """Test parsing task with priority indicators."""
        data = {'text': 'Important meeting !!'}
        
        response = client.post('/api/tasks/parse',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert response_data['parsed']['title'] == 'Important meeting'
        assert response_data['parsed']['priority'] == 2  # Medium priority
    
    def test_parse_task_with_tags(self, client, auth_headers):
        """Test parsing task with hashtag tags."""
        data = {'text': 'Buy groceries #shopping #food'}
        
        response = client.post('/api/tasks/parse',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert response_data['parsed']['title'] == 'Buy groceries'
        assert 'tags' in response_data['parsed']
        assert 'shopping' in response_data['parsed']['tags']
        assert 'food' in response_data['parsed']['tags']
    
    def test_parse_task_missing_text(self, client, auth_headers):
        """Test parsing without text field."""
        data = {}
        
        response = client.post('/api/tasks/parse',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Text is required' in response_data['error']
    
    def test_parse_task_unauthorized(self, client):
        """Test parsing without authentication."""
        data = {'text': 'Some task'}
        
        response = client.post('/api/tasks/parse',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 401
    
    def test_create_task_with_nlp(self, client, auth_headers):
        """Test creating task with NLP parsing enabled."""
        data = {
            'title': 'Meeting tomorrow #work !!',
            'use_nlp': True
        }
        
        response = client.post('/api/tasks',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        
        # Title should be cleaned up
        assert 'Meeting' in response_data['task']['title']
        # Should have medium priority from !!
        assert response_data['task']['priority'] == 2
        # Should have work tag
        tag_names = [tag['name'] for tag in response_data['task']['tags']]
        assert 'work' in tag_names

