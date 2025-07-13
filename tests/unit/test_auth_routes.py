"""
Unit tests for authentication routes.
"""
import pytest
import json
from src.models.user import User, db


class TestAuthRoutes:
    """Test cases for authentication endpoints."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        
        assert 'message' in response_data
        assert 'access_token' in response_data
        assert 'user' in response_data
        assert response_data['user']['username'] == 'newuser'
        assert response_data['user']['email'] == 'newuser@example.com'
        assert 'password_hash' not in response_data['user']
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        # Missing username
        data = {'email': 'test@example.com', 'password': 'password123'}
        response = client.post('/api/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        assert response.status_code == 400
        
        # Missing email
        data = {'username': 'testuser', 'password': 'password123'}
        response = client.post('/api/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        assert response.status_code == 400
        
        # Missing password
        data = {'username': 'testuser', 'email': 'test@example.com'}
        response = client.post('/api/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username."""
        data = {
            'username': 'testuser',  # Same as test_user
            'email': 'different@example.com',
            'password': 'password123'
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Username already exists' in response_data['error']
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        data = {
            'username': 'differentuser',
            'email': 'test@example.com',  # Same as test_user
            'password': 'password123'
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Email already exists' in response_data['error']
    
    def test_login_success(self, client, test_user):
        """Test successful user login."""
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'message' in response_data
        assert 'access_token' in response_data
        assert 'user' in response_data
        assert response_data['user']['username'] == 'testuser'
        assert 'password_hash' not in response_data['user']
    
    def test_login_missing_fields(self, client):
        """Test login with missing required fields."""
        # Missing username
        data = {'password': 'password123'}
        response = client.post('/api/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        assert response.status_code == 400
        
        # Missing password
        data = {'username': 'testuser'}
        response = client.post('/api/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_login_invalid_username(self, client):
        """Test login with invalid username."""
        data = {
            'username': 'nonexistentuser',
            'password': 'password123'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert 'Invalid username or password' in response_data['error']
    
    def test_login_invalid_password(self, client, test_user):
        """Test login with invalid password."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert 'Invalid username or password' in response_data['error']
    
    def test_get_current_user_success(self, client, auth_headers):
        """Test getting current user with valid token."""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'user' in response_data
        assert response_data['user']['username'] == 'testuser'
        assert 'password_hash' not in response_data['user']
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/auth/me', headers=headers)
        
        assert response.status_code == 422  # Unprocessable Entity for invalid JWT
    
    def test_jwt_token_format(self, client, test_user):
        """Test that JWT token contains correct subject format."""
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        # Token should be present and be a string
        token = response_data['access_token']
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Token should have 3 parts (header.payload.signature)
        token_parts = token.split('.')
        assert len(token_parts) == 3
    
    def test_register_creates_user_in_database(self, client):
        """Test that registration actually creates user in database."""
        data = {
            'username': 'dbuser',
            'email': 'dbuser@example.com',
            'password': 'password123'
        }
        
        # Check user doesn't exist before
        with client.application.app_context():
            assert User.query.filter_by(username='dbuser').first() is None
        
        response = client.post('/api/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        # Check user exists after registration
        with client.application.app_context():
            user = User.query.filter_by(username='dbuser').first()
            assert user is not None
            assert user.email == 'dbuser@example.com'
            assert user.check_password('password123')
    
    def test_login_with_email_not_supported(self, client, test_user):
        """Test that login with email instead of username fails."""
        data = {
            'username': 'test@example.com',  # Using email as username
            'password': 'testpassword123'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 401  # Should fail since we expect username

