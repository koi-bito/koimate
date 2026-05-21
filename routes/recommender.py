from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, UserInput
from services.ml_pipeline import recommender

recommender_bp = Blueprint('recommender', __name__)

@recommender_bp.route('/', methods=['POST'])
@jwt_required(optional=True) # Allow optional JWT so we can demo easily if needed
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
        user_input = UserInput(
            user_id=current_user_id,
            purchases_text=purchases,
            needs_text=needs,
            shortages_text=shortages
        )
        db.session.add(user_input)
        db.session.commit()

    # Get recommendations
    recommended_products = recommender.recommend(query)
    
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
