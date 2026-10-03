from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from models import db, UserInput, Review
from services.ml_pipeline import recommender

recommender_bp = Blueprint('recommender', __name__)


@recommender_bp.route('/', methods=['POST'])
@jwt_required(optional=True)  # Allow optional JWT so we can demo easily if needed
def get_recommendations():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    purchases = data.get('purchases', '')
    needs = data.get('needs', '')
    shortages = data.get('shortages', '')

    query = f"{purchases} {needs} {shortages}"

    if not query.strip():
        return jsonify({"msg": "Please provide purchases, needs, or shortages."}), 400

    # Save user input if authenticated
    current_user_id = get_jwt_identity()
    if current_user_id:
        current_user_id = int(current_user_id)
        user_input = UserInput(
            user_id=current_user_id,
            purchases_text=purchases,
            needs_text=needs,
            shortages_text=shortages
        )
        db.session.add(user_input)
        db.session.commit()

    # Get recommendations from ML pipeline
    recommended_products = recommender.recommend(query)

    # Re-rank using average ratings from reviews
    if recommended_products:
        product_ids = [p.id for p in recommended_products]
        n = len(recommended_products)

        # Fetch average ratings for candidate products
        avg_ratings_query = db.session.query(
            Review.product_id, func.avg(Review.rating)
        ).filter(Review.product_id.in_(product_ids))\
         .group_by(Review.product_id).all()

        avg_ratings_map = {row[0]: float(row[1]) for row in avg_ratings_query}

        # Build scored list: behavioral_score from position, blended with rating
        scored = []
        for i, p in enumerate(recommended_products):
            # Position-based score: first item gets 1.0, last gets close to 0
            behavioral_score = 1.0 - (i / n) if n > 1 else 1.0
            avg_rating = avg_ratings_map.get(p.id, 3.0)  # default neutral
            normalized_avg_rating = avg_rating / 5.0
            final_score = behavioral_score * 0.85 + normalized_avg_rating * 0.15
            scored.append((p, final_score))

        # Sort descending by final score
        scored.sort(key=lambda x: x[1], reverse=True)
        recommended_products = [item[0] for item in scored]

    result = []
    for p in recommended_products:
        result.append({
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "description": p.description,
            "price": p.price,
            "image_url": p.image_url
        })

    return jsonify({"recommendations": result})
