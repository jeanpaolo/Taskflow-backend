"""
Unit tests for project routes.
"""
import pytest
import json
from src.models.user import Project, db


class TestProjectRoutes:
    """Test cases for project endpoints."""
    
    def test_get_projects_empty(self, client, auth_headers):
        """Test getting projects when user has none."""
        response = client.get('/api/projects', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'projects' in response_data
        assert response_data['projects'] == []
    
    def test_get_projects_with_data(self, client, auth_headers, test_project):
        """Test getting projects when user has projects."""
        response = client.get('/api/projects', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'projects' in response_data
        assert len(response_data['projects']) == 1
        assert response_data['projects'][0]['name'] == 'Test Project'
        assert response_data['projects'][0]['description'] == 'A test project'
        assert response_data['projects'][0]['color'] == '#3B82F6'
    
    def test_get_projects_unauthorized(self, client):
        """Test getting projects without authentication."""
        response = client.get('/api/projects')
        assert response.status_code == 401
    
    def test_create_project_success(self, client, auth_headers):
        """Test successful project creation."""
        data = {
            'name': 'New Project',
            'description': 'A new project description',
            'color': '#FF5733'
        }
        
        response = client.post('/api/projects',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        
        assert 'message' in response_data
        assert 'project' in response_data
        assert response_data['project']['name'] == 'New Project'
        assert response_data['project']['description'] == 'A new project description'
        assert response_data['project']['color'] == '#FF5733'
        assert response_data['project']['task_count'] == 0
    
    def test_create_project_minimal_data(self, client, auth_headers):
        """Test creating project with minimal required data."""
        data = {'name': 'Minimal Project'}
        
        response = client.post('/api/projects',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        
        assert response_data['project']['name'] == 'Minimal Project'
        assert response_data['project']['description'] == ''  # Default empty
        assert response_data['project']['color'] == '#3B82F6'  # Default color
    
    def test_create_project_missing_name(self, client, auth_headers):
        """Test creating project without required name field."""
        data = {'description': 'Project without name'}
        
        response = client.post('/api/projects',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Name is required' in response_data['error']
    
    def test_create_project_unauthorized(self, client):
        """Test creating project without authentication."""
        data = {'name': 'Unauthorized Project'}
        
        response = client.post('/api/projects',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 401
    
    def test_get_single_project_success(self, client, auth_headers, test_project):
        """Test getting a single project by ID."""
        response = client.get(f'/api/projects/{test_project.id}', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'project' in response_data
        assert response_data['project']['id'] == test_project.id
        assert response_data['project']['name'] == 'Test Project'
    
    def test_get_single_project_not_found(self, client, auth_headers):
        """Test getting a non-existent project."""
        response = client.get('/api/projects/999', headers=auth_headers)
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'Project not found' in response_data['error']
    
    def test_get_single_project_unauthorized(self, client, test_project):
        """Test getting a project without authentication."""
        response = client.get(f'/api/projects/{test_project.id}')
        assert response.status_code == 401
    
    def test_update_project_success(self, client, auth_headers, test_project):
        """Test successful project update."""
        data = {
            'name': 'Updated Project',
            'description': 'Updated description',
            'color': '#00FF00'
        }
        
        response = client.put(f'/api/projects/{test_project.id}',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'message' in response_data
        assert 'project' in response_data
        assert response_data['project']['name'] == 'Updated Project'
        assert response_data['project']['description'] == 'Updated description'
        assert response_data['project']['color'] == '#00FF00'
    
    def test_update_project_partial(self, client, auth_headers, test_project):
        """Test partial project update."""
        data = {'name': 'Partially Updated'}
        
        response = client.put(f'/api/projects/{test_project.id}',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert response_data['project']['name'] == 'Partially Updated'
        # Other fields should remain unchanged
        assert response_data['project']['description'] == 'A test project'
        assert response_data['project']['color'] == '#3B82F6'
    
    def test_update_project_not_found(self, client, auth_headers):
        """Test updating a non-existent project."""
        data = {'name': 'Updated Project'}
        
        response = client.put('/api/projects/999',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'Project not found' in response_data['error']
    
    def test_update_project_unauthorized(self, client, test_project):
        """Test updating a project without authentication."""
        data = {'name': 'Unauthorized Update'}
        
        response = client.put(f'/api/projects/{test_project.id}',
                            data=json.dumps(data),
                            content_type='application/json')
        
        assert response.status_code == 401
    
    def test_delete_project_success(self, client, auth_headers, test_project):
        """Test successful project deletion."""
        project_id = test_project.id
        
        response = client.delete(f'/api/projects/{project_id}', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'Project deleted successfully' in response_data['message']
        
        # Verify project is actually deleted
        with client.application.app_context():
            deleted_project = Project.query.get(project_id)
            assert deleted_project is None
    
    def test_delete_project_not_found(self, client, auth_headers):
        """Test deleting a non-existent project."""
        response = client.delete('/api/projects/999', headers=auth_headers)
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'Project not found' in response_data['error']
    
    def test_delete_project_unauthorized(self, client, test_project):
        """Test deleting a project without authentication."""
        response = client.delete(f'/api/projects/{test_project.id}')
        assert response.status_code == 401
    
    def test_projects_user_isolation(self, client, multiple_users):
        """Test that users can only access their own projects."""
        with client.application.app_context():
            # Create projects for different users
            user1, user2, user3 = multiple_users
            
            project1 = Project(name='User1 Project', user_id=user1.id)
            project2 = Project(name='User2 Project', user_id=user2.id)
            
            db.session.add_all([project1, project2])
            db.session.commit()
            
            # Create tokens for each user
            from flask_jwt_extended import create_access_token
            token1 = create_access_token(identity=str(user1.id))
            token2 = create_access_token(identity=str(user2.id))
            
            headers1 = {'Authorization': f'Bearer {token1}'}
            headers2 = {'Authorization': f'Bearer {token2}'}
            
            # User1 should only see their project
            response = client.get('/api/projects', headers=headers1)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['projects']) == 1
            assert data['projects'][0]['name'] == 'User1 Project'
            
            # User2 should only see their project
            response = client.get('/api/projects', headers=headers2)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['projects']) == 1
            assert data['projects'][0]['name'] == 'User2 Project'
            
            # User1 should not be able to access User2's project
            response = client.get(f'/api/projects/{project2.id}', headers=headers1)
            assert response.status_code == 404
    
    def test_project_creation_in_database(self, client, auth_headers):
        """Test that project creation actually saves to database."""
        data = {
            'name': 'Database Test Project',
            'description': 'Testing database persistence',
            'color': '#123456'
        }
        
        response = client.post('/api/projects',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        project_id = response_data['project']['id']
        
        # Verify project exists in database
        with client.application.app_context():
            project = Project.query.get(project_id)
            assert project is not None
            assert project.name == 'Database Test Project'
            assert project.description == 'Testing database persistence'
            assert project.color == '#123456'

