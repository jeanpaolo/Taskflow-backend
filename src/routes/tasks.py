from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, Task, Project, Tag
from datetime import datetime
import re

tasks_bp = Blueprint('tasks', __name__)

def parse_natural_language(text):
    """Simple natural language processing for task creation"""
    result = {'title': text.strip()}
    
    # Parse due dates
    date_patterns = [
        (r'\b(today)\b', lambda: datetime.now().date()),
        (r'\b(tomorrow)\b', lambda: datetime.now().date().replace(day=datetime.now().day + 1)),
        (r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', 
         lambda match: get_next_weekday(match.group(1)))
    ]
    
    for pattern, date_func in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                result['due_date'] = date_func() if callable(date_func) else date_func(match)
                result['title'] = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
                break
            except:
                pass
    
    # Parse tags
    tag_matches = re.findall(r'#(\w+)', text)
    if tag_matches:
        result['tags'] = tag_matches
        result['title'] = re.sub(r'#\w+', '', result['title']).strip()
    
    # Parse priority
    if '!!!' in text:
        result['priority'] = 3  # High
        result['title'] = result['title'].replace('!!!', '').strip()
    elif '!!' in text:
        result['priority'] = 2  # Medium
        result['title'] = result['title'].replace('!!', '').strip()
    
    return result

def get_next_weekday(day_name):
    """Get the next occurrence of a weekday"""
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    today = datetime.now().date()
    today_weekday = today.weekday()
    target_weekday = days.index(day_name.lower())
    
    days_ahead = target_weekday - today_weekday
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    
    return today.replace(day=today.day + days_ahead)

@tasks_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        
        # Get query parameters
        project_id = request.args.get('project_id')
        completed = request.args.get('completed')
        priority = request.args.get('priority')
        tag_id = request.args.get('tag_id')
        
        # Build query
        query = Task.query.filter_by(user_id=user_id)
        
        if project_id:
            query = query.filter_by(project_id=project_id)
        
        if completed is not None:
            query = query.filter_by(completed=completed.lower() == 'true')
        
        if priority:
            query = query.filter_by(priority=int(priority))
        
        if tag_id:
            query = query.filter(Task.tags.any(id=tag_id))
        
        tasks = query.order_by(Task.created_at.desc()).all()
        
        return jsonify({
            'tasks': [task.to_dict() for task in tasks]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        # Parse natural language if enabled
        if data.get('use_nlp', False):
            parsed = parse_natural_language(data['title'])
            data.update(parsed)
        
        # Create task
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 1),
            project_id=data.get('project_id'),
            user_id=user_id
        )
        
        # Set due date
        if data.get('due_date'):
            if isinstance(data['due_date'], str):
                task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            else:
                task.due_date = data['due_date']
        
        db.session.add(task)
        db.session.flush()  # Get the task ID
        
        # Add tags
        if data.get('tags'):
            for tag_name in data['tags']:
                tag = Tag.query.filter_by(name=tag_name, user_id=user_id).first()
                if not tag:
                    tag = Tag(name=tag_name, user_id=user_id)
                    db.session.add(tag)
                task.tags.append(tag)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Task created successfully',
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({'task': task.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'completed' in data:
            task.completed = data['completed']
        if 'priority' in data:
            task.priority = data['priority']
        if 'project_id' in data:
            task.project_id = data['project_id']
        if 'due_date' in data:
            if data['due_date']:
                task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            else:
                task.due_date = None
        
        # Update tags
        if 'tags' in data:
            task.tags.clear()
            for tag_name in data['tags']:
                tag = Tag.query.filter_by(name=tag_name, user_id=user_id).first()
                if not tag:
                    tag = Tag(name=tag_name, user_id=user_id)
                    db.session.add(tag)
                task.tags.append(tag)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks/parse', methods=['POST'])
@jwt_required()
def parse_task():
    try:
        data = request.get_json()
        
        if not data or not data.get('text'):
            return jsonify({'error': 'Text is required'}), 400
        
        parsed = parse_natural_language(data['text'])
        
        return jsonify({'parsed': parsed}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

