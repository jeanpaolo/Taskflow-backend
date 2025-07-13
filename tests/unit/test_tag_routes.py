"""
Unit tests for tag routes.
"""
import pytest
import json
from src.models.user import Tag, db


class TestTagRoutes:
    """Test cases for tag endpoints."""
    
    def test_get_tags_empty(self, client, auth_headers):
        """Test getting tags when user has none."""
        response = client.get('/api/tags', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'tags' in response_data
        assert response_data['tags'] == []
    
    def test_get_tags_with_data(self, client, auth_headers, test_tag):
        """Test getting tags when user has tags."""
        response = client.get('/api/tags', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'tags' in response_data
        assert len(response_data['tags']) == 1
        assert response_data['tags'][0]['name'] == 'Test Tag'
        assert response_data['tags'][0]['color'] == '#10B981'
    
    def test_get_tags_unauthorized(self, client):
        """Test getting tags without authentication."""
        response = client.get('/api/tags')
        assert response.status_code == 401
    
    def test_create_tag_success(self, client, auth_headers):
        """Test successful tag creation."""
        data = {
            'name': 'Important',
            'color': '#FF0000'
        }
        
        response = client.post('/api/tags',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        
        assert 'message' in response_data
        assert 'tag' in response_data
        assert response_data['tag']['name'] == 'Important'
        assert response_data['tag']['color'] == '#FF0000'
    
    def test_create_tag_minimal_data(self, client, auth_headers):
        """Test creating tag with minimal required data."""
        data = {'name': 'Minimal Tag'}
        
        response = client.post('/api/tags',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        
        assert response_data['tag']['name'] == 'Minimal Tag'
        assert response_data['tag']['color'] == '#6B7280'  # Default color
    
    def test_create_tag_missing_name(self, client, auth_headers):
        """Test creating tag without required name field."""
        data = {'color': '#FF0000'}
        
        response = client.post('/api/tags',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Name is required' in response_data['error']
    
    def test_create_tag_duplicate_name(self, client, auth_headers, test_tag):
        """Test creating tag with duplicate name for same user."""
        data = {
            'name': 'Test Tag',  # Same as test_tag
            'color': '#FF0000'
        }
        
        response = client.post('/api/tags',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Tag already exists' in response_data['error']
    
    def test_create_tag_unauthorized(self, client):
        """Test creating tag without authentication."""
        data = {'name': 'Unauthorized Tag'}
        
        response = client.post('/api/tags',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 401
    
    def test_update_tag_success(self, client, auth_headers, test_tag):
        """Test successful tag update."""
        data = {
            'name': 'Updated Tag',
            'color': '#00FF00'
        }
        
        response = client.put(f'/api/tags/{test_tag.id}',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'message' in response_data
        assert 'tag' in response_data
        assert response_data['tag']['name'] == 'Updated Tag'
        assert response_data['tag']['color'] == '#00FF00'
    
    def test_update_tag_partial(self, client, auth_headers, test_tag):
        """Test partial tag update."""
        data = {'name': 'Partially Updated'}
        
        response = client.put(f'/api/tags/{test_tag.id}',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert response_data['tag']['name'] == 'Partially Updated'
        # Color should remain unchanged
        assert response_data['tag']['color'] == '#10B981'
    
    def test_update_tag_duplicate_name(self, client, auth_headers, test_user):
        """Test updating tag to duplicate name."""
        with client.application.app_context():
            # Create two tags
            tag1 = Tag(name='Tag One', user_id=test_user.id)
            tag2 = Tag(name='Tag Two', user_id=test_user.id)
            db.session.add_all([tag1, tag2])
            db.session.commit()
            
            # Try to update tag2 to have same name as tag1
            data = {'name': 'Tag One'}
            
            response = client.put(f'/api/tags/{tag2.id}',
                                data=json.dumps(data),
                                content_type='application/json',
                                headers=auth_headers)
            
            assert response.status_code == 400
            response_data = json.loads(response.data)
            assert 'Tag name already exists' in response_data['error']
    
    def test_update_tag_not_found(self, client, auth_headers):
        """Test updating a non-existent tag."""
        data = {'name': 'Updated Tag'}
        
        response = client.put('/api/tags/999',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'Tag not found' in response_data['error']
    
    def test_update_tag_unauthorized(self, client, test_tag):
        """Test updating a tag without authentication."""
        data = {'name': 'Unauthorized Update'}
        
        response = client.put(f'/api/tags/{test_tag.id}',
                            data=json.dumps(data),
                            content_type='application/json')
        
        assert response.status_code == 401
    
    def test_delete_tag_success(self, client, auth_headers, test_tag):
        """Test successful tag deletion."""
        tag_id = test_tag.id
        
        response = client.delete(f'/api/tags/{tag_id}', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'Tag deleted successfully' in response_data['message']
        
        # Verify tag is actually deleted
        with client.application.app_context():
            deleted_tag = Tag.query.get(tag_id)
            assert deleted_tag is None
    
    def test_delete_tag_not_found(self, client, auth_headers):
        """Test deleting a non-existent tag."""
        response = client.delete('/api/tags/999', headers=auth_headers)
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'Tag not found' in response_data['error']
    
    def test_delete_tag_unauthorized(self, client, test_tag):
        """Test deleting a tag without authentication."""
        response = client.delete(f'/api/tags/{test_tag.id}')
        assert response.status_code == 401
    
    def test_tags_user_isolation(self, client, multiple_users):
        """Test that users can only access their own tags."""
        with client.application.app_context():
            # Create tags for different users
            user1, user2, user3 = multiple_users
            
            tag1 = Tag(name='User1 Tag', user_id=user1.id)
            tag2 = Tag(name='User2 Tag', user_id=user2.id)
            
            db.session.add_all([tag1, tag2])
            db.session.commit()
            
            # Create tokens for each user
            from flask_jwt_extended import create_access_token
            token1 = create_access_token(identity=str(user1.id))
            token2 = create_access_token(identity=str(user2.id))
            
            headers1 = {'Authorization': f'Bearer {token1}'}
            headers2 = {'Authorization': f'Bearer {token2}'}
            
            # User1 should only see their tag
            response = client.get('/api/tags', headers=headers1)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['tags']) == 1
            assert data['tags'][0]['name'] == 'User1 Tag'
            
            # User2 should only see their tag
            response = client.get('/api/tags', headers=headers2)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['tags']) == 1
            assert data['tags'][0]['name'] == 'User2 Tag'
            
            # User1 should not be able to access User2's tag
            response = client.put(f'/api/tags/{tag2.id}',
                                data=json.dumps({'name': 'Hacked'}),
                                content_type='application/json',
                                headers=headers1)
            assert response.status_code == 404
    
    def test_tag_creation_in_database(self, client, auth_headers):
        """Test that tag creation actually saves to database."""
        data = {
            'name': 'Database Test Tag',
            'color': '#ABCDEF'
        }
        
        response = client.post('/api/tags',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        tag_id = response_data['tag']['id']
        
        # Verify tag exists in database
        with client.application.app_context():
            tag = Tag.query.get(tag_id)
            assert tag is not None
            assert tag.name == 'Database Test Tag'
            assert tag.color == '#ABCDEF'
    
    def test_tags_alphabetical_order(self, client, auth_headers, test_user):
        """Test that tags are returned in alphabetical order."""
        with client.application.app_context():
            # Create tags in non-alphabetical order
            tags = [
                Tag(name='Zebra', user_id=test_user.id),
                Tag(name='Alpha', user_id=test_user.id),
                Tag(name='Beta', user_id=test_user.id)
            ]
            db.session.add_all(tags)
            db.session.commit()
            
            response = client.get('/api/tags', headers=auth_headers)
            assert response.status_code == 200
            
            response_data = json.loads(response.data)
            tag_names = [tag['name'] for tag in response_data['tags']]
            
            # Should be in alphabetical order
            assert tag_names == ['Alpha', 'Beta', 'Zebra']
    
    def test_duplicate_tag_names_different_users(self, client, multiple_users):
        """Test that different users can have tags with the same name."""
        with client.application.app_context():
            user1, user2, user3 = multiple_users
            
            # Create tokens for each user
            from flask_jwt_extended import create_access_token
            token1 = create_access_token(identity=str(user1.id))
            token2 = create_access_token(identity=str(user2.id))
            
            headers1 = {'Authorization': f'Bearer {token1}'}
            headers2 = {'Authorization': f'Bearer {token2}'}
            
            # Both users create a tag with the same name
            data = {'name': 'Important', 'color': '#FF0000'}
            
            response1 = client.post('/api/tags',
                                  data=json.dumps(data),
                                  content_type='application/json',
                                  headers=headers1)
            assert response1.status_code == 201
            
            response2 = client.post('/api/tags',
                                  data=json.dumps(data),
                                  content_type='application/json',
                                  headers=headers2)
            assert response2.status_code == 201
            
            # Both should succeed since they're for different users
            assert json.loads(response1.data)['tag']['name'] == 'Important'
            assert json.loads(response2.data)['tag']['name'] == 'Important'

