from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, UserBehavior

tracking_bp = Blueprint('tracking', __name__)

@tracking_bp.route('/', methods=['POST'])
@jwt_required(optional=True)
def track_behavior():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    product_id = data.get('product_id')
    action_type = data.get('action_type') # e.g., 'view', 'add_to_cart', 'purchase'
    
    if not product_id or not action_type:
        return jsonify({"msg": "product_id and action_type are required"}), 400

    current_user_id = get_jwt_identity()
    if not current_user_id:
        # If not logged in, we could track anonymously or just ignore. We'll ignore for now.
        return jsonify({"msg": "User not authenticated, behavior not tracked"}), 200

    behavior = UserBehavior(
        user_id=current_user_id,
        product_id=product_id,
        action_type=action_type
    )
    db.session.add(behavior)
    db.session.commit()

    return jsonify({"msg": "Behavior tracked successfully"}), 201
