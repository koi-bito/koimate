from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func, case
from models import db, UserBehavior, Product, Review

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


@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    # 1. Top 10 products by total interactions (views + cart + purchases)
    top_products_query = db.session.query(
        Product.id,
        Product.name,
        func.sum(case(
            (UserBehavior.action_type == 'view', 1),
            else_=0
        )).label('view_count'),
        func.sum(case(
            (UserBehavior.action_type == 'add_to_cart', 1),
            else_=0
        )).label('cart_count'),
        func.sum(case(
            (UserBehavior.action_type == 'purchase', 1),
            else_=0
        )).label('purchase_count'),
        func.count(UserBehavior.id).label('total_interactions')
    ).join(UserBehavior, Product.id == UserBehavior.product_id)\
     .group_by(Product.id, Product.name)\
     .order_by(func.count(UserBehavior.id).desc())\
     .limit(10).all()

    top_products = []
    for row in top_products_query:
        top_products.append({
            "product_id": row[0],
            "name": row[1],
            "view_count": int(row[2]),
            "cart_count": int(row[3]),
            "purchase_count": int(row[4])
        })

    # 2. Top 10 products by average rating
    avg_ratings_query = db.session.query(
        Product.id,
        Product.name,
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('review_count')
    ).join(Review, Product.id == Review.product_id)\
     .group_by(Product.id, Product.name)\
     .order_by(func.avg(Review.rating).desc())\
     .limit(10).all()

    avg_ratings = []
    for row in avg_ratings_query:
        avg_ratings.append({
            "product_id": row[0],
            "name": row[1],
            "avg_rating": round(float(row[2]), 1),
            "review_count": int(row[3])
        })

    # 3. Interaction trend over time (daily views and purchases)
    trend_query = db.session.query(
        func.date(UserBehavior.timestamp).label('date'),
        func.sum(case(
            (UserBehavior.action_type == 'view', 1),
            else_=0
        )).label('views'),
        func.sum(case(
            (UserBehavior.action_type == 'purchase', 1),
            else_=0
        )).label('purchases')
    ).group_by(func.date(UserBehavior.timestamp))\
     .order_by(func.date(UserBehavior.timestamp)).all()

    interaction_trend = []
    for row in trend_query:
        interaction_trend.append({
            "date": str(row[0]),
            "views": int(row[1]),
            "purchases": int(row[2])
        })

    return jsonify({
        "top_products": top_products,
        "avg_ratings": avg_ratings,
        "interaction_trend": interaction_trend
    })
