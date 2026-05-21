import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from models import Product, db

class RecommenderSystem:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.knn = NearestNeighbors(n_neighbors=5, metric='cosine')
        self.product_ids = []
        self.is_fitted = False

    def fit(self):
        products = Product.query.all()
        if not products:
            return False
            
        corpus = []
        self.product_ids = []
        
        for p in products:
            text = f"{p.name} {p.category} {p.description} {p.features_text or ''}"
            corpus.append(text)
            self.product_ids.append(p.id)
            
        if not corpus:
            return False

        # Fit TF-IDF
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        
        # Fit KNN
        self.knn.fit(tfidf_matrix)
        self.is_fitted = True
        return True

    def recommend(self, query, n_recommendations=5):
        if not self.is_fitted:
            # Try fitting if not already
            if not self.fit():
                return []
                
        # Adjust n_neighbors if we have fewer products than requested
        k = min(n_recommendations, len(self.product_ids))
        if k == 0:
            return []

        # Vectorize user query
        query_vec = self.vectorizer.transform([query])
        
        # Find nearest neighbors
        distances, indices = self.knn.kneighbors(query_vec, n_neighbors=k)
        
        # Retrieve recommended product IDs
        recommended_ids = [self.product_ids[idx] for idx in indices[0]]
        
        # Fetch actual products from DB
        recommended_products = Product.query.filter(Product.id.in_(recommended_ids)).all()
        
        # Sort them in the order of recommendation
        product_dict = {p.id: p for p in recommended_products}
        ordered_products = [product_dict[p_id] for p_id in recommended_ids if p_id in product_dict]
        
        return ordered_products

# Singleton instance
recommender = RecommenderSystem()
