from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, Tag

tags_bp = Blueprint('tags', __name__)

@tags_bp.route('/tags', methods=['GET'])
@jwt_required()
def get_tags():
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        tags = Tag.query.filter_by(user_id=user_id).order_by(Tag.name).all()
        
        return jsonify({
            'tags': [tag.to_dict() for tag in tags]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tags_bp.route('/tags', methods=['POST'])
@jwt_required()
def create_tag():
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        # Check if tag already exists
        existing_tag = Tag.query.filter_by(name=data['name'], user_id=user_id).first()
        if existing_tag:
            return jsonify({'error': 'Tag already exists'}), 400
        
        tag = Tag(
            name=data['name'],
            color=data.get('color', '#6B7280'),
            user_id=user_id
        )
        
        db.session.add(tag)
        db.session.commit()
        
        return jsonify({
            'message': 'Tag created successfully',
            'tag': tag.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tags_bp.route('/tags/<int:tag_id>', methods=['PUT'])
@jwt_required()
def update_tag(tag_id):
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first()
        
        if not tag:
            return jsonify({'error': 'Tag not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            # Check if new name already exists
            existing_tag = Tag.query.filter_by(name=data['name'], user_id=user_id).first()
            if existing_tag and existing_tag.id != tag_id:
                return jsonify({'error': 'Tag name already exists'}), 400
            tag.name = data['name']
        
        if 'color' in data:
            tag.color = data['color']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Tag updated successfully',
            'tag': tag.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tags_bp.route('/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first()
        
        if not tag:
            return jsonify({'error': 'Tag not found'}), 404
        
        db.session.delete(tag)
        db.session.commit()
        
        return jsonify({'message': 'Tag deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

