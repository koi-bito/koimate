from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Review, Product

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/', methods=['POST'])
@jwt_required()
def submit_review():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    product_id = data.get('product_id')
    rating = data.get('rating')
    review_text = data.get('review_text', '')

    if not product_id or rating is None:
        return jsonify({"msg": "product_id and rating are required"}), 400

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"msg": "Rating must be an integer between 1 and 5"}), 400

    # Verify product exists
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"msg": "Product not found"}), 404

    current_user_id = int(get_jwt_identity())

    # Check if review already exists — update instead of error
    existing = Review.query.filter_by(user_id=current_user_id, product_id=product_id).first()

    if existing:
        existing.rating = rating
        existing.review_text = review_text
        db.session.commit()
        return jsonify({"msg": "Review updated successfully"}), 200
    else:
        review = Review(
            user_id=current_user_id,
            product_id=product_id,
            rating=rating,
            review_text=review_text
        )
        db.session.add(review)
        db.session.commit()
        return jsonify({"msg": "Review submitted successfully"}), 201


@reviews_bp.route('/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()

    result = []
    for r in reviews:
        result.append({
            "id": r.id,
            "user_id": r.user_id,
            "product_id": r.product_id,
            "rating": r.rating,
            "review_text": r.review_text,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })

    return jsonify({"reviews": result})


@reviews_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_reviews():
    current_user_id = int(get_jwt_identity())
    reviews = Review.query.filter_by(user_id=current_user_id).order_by(Review.created_at.desc()).all()

    result = []
    for r in reviews:
        product = Product.query.get(r.product_id)
        result.append({
            "id": r.id,
            "product_id": r.product_id,
            "product_name": product.name if product else None,
            "rating": r.rating,
            "review_text": r.review_text,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })

    return jsonify({"reviews": result})
