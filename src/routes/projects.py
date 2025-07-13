from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, Project

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        projects = Project.query.filter_by(user_id=user_id).order_by(Project.created_at.desc()).all()
        
        return jsonify({
            'projects': [project.to_dict() for project in projects]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        project = Project(
            name=data['name'],
            description=data.get('description', ''),
            color=data.get('color', '#3B82F6'),
            user_id=user_id
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'message': 'Project created successfully',
            'project': project.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({'project': project.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            project.name = data['name']
        if 'description' in data:
            project.description = data['description']
        if 'color' in data:
            project.color = data['color']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': project.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'message': 'Project deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

