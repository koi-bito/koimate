from flask import Blueprint, jsonify
from sqlalchemy import func
from models import db, UserBehavior, Product

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/data', methods=['GET'])
def get_analytics_data():
    # 1. Most viewed/interacted categories
    category_counts = db.session.query(
        Product.category, func.count(UserBehavior.id)
    ).join(UserBehavior, Product.id == UserBehavior.product_id)\
     .group_by(Product.category).all()
     
    categories = [row[0] for row in category_counts]
    cat_counts = [row[1] for row in category_counts]

    # 2. Interactions over time (by date)
    date_counts = db.session.query(
        func.date(UserBehavior.timestamp), func.count(UserBehavior.id)
    ).group_by(func.date(UserBehavior.timestamp)).all()
    
    dates = [str(row[0]) for row in date_counts]
    d_counts = [row[1] for row in date_counts]
    
    # 3. Action types distribution
    action_counts = db.session.query(
        UserBehavior.action_type, func.count(UserBehavior.id)
    ).group_by(UserBehavior.action_type).all()
    
    actions = [row[0] for row in action_counts]
    a_counts = [row[1] for row in action_counts]

    return jsonify({
        "categories": {"labels": categories, "data": cat_counts},
        "timeline": {"labels": dates, "data": d_counts},
        "actions": {"labels": actions, "data": a_counts}
    })
