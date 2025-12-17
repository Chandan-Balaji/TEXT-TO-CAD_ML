"""
AI-Powered Text-to-CAD Backend with Multi-Object Support
Uses sklearn ML models: Random Forest, Linear Regression, K-Means
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import os
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# ==========================
# ML MODELS & TRAINING DATA
# ==========================

class TextToCADModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.shape_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.size_predictor = LinearRegression()
        self.radius_predictor = LinearRegression()
        self.height_predictor = LinearRegression()
        self.position_clusterer = KMeans(n_clusters=8, random_state=42)
        
        # Training data storage
        self.training_data = []
        self.trained = False
        
        # Load existing data if available
        self.load_training_data()
        
        # Initialize with default training data
        if not self.trained:
            self.init_default_training()
   
    def init_default_training(self):
        """Initialize with basic training examples"""
        default_data = [
            # Spheres
            {"text": "red sphere", "shape": "sphere", "size": 1, "radius": 1, "height": 2, "color": 0xff4444, "position": [0,0,0]},
            {"text": "large ball", "shape": "sphere", "size": 2, "radius": 2, "height": 2, "color": 0x667eea, "position": [0,0,0]},
            {"text": "small orb", "shape": "sphere", "size": 0.5, "radius": 0.5, "height": 2, "color": 0x667eea, "position": [0,0,0]},
            {"text": "blue globe", "shape": "sphere", "size": 1.5, "radius": 1.5, "height": 2, "color": 0x4444ff, "position": [0,0,0]},
            
            # Cubes
            {"text": "cube", "shape": "cube", "size": 1, "radius": 1, "height": 2, "color": 0x667eea, "position": [0,0,0]},
            {"text": "big box", "shape": "cube", "size": 2, "radius": 1, "height": 2, "color": 0x667eea, "position": [0,0,0]},
            {"text": "small block", "shape": "cube", "size": 0.5, "radius": 1, "height": 2, "color": 0x667eea, "position": [0,0,0]},
            {"text": "green square", "shape": "cube", "size": 1, "radius": 1, "height": 2, "color": 0x44ff44, "position": [0,0,0]},
            
            # Cylinders
            {"text": "cylinder", "shape": "cylinder", "size": 1, "radius": 1, "height": 3, "color": 0x667eea, "position": [0,0,0]},
            {"text": "tall tube", "shape": "cylinder", "size": 1, "radius": 0.8, "height": 4, "color": 0x667eea, "position": [0,0,0]},
            {"text": "pipe", "shape": "cylinder", "size": 1, "radius": 0.5, "height": 3, "color": 0x667eea, "position": [0,0,0]},
            {"text": "column", "shape": "cylinder", "size": 1.5, "radius": 1, "height": 5, "color": 0x667eea, "position": [0,0,0]},
            
            # Cones
            {"text": "cone", "shape": "cone", "size": 1, "radius": 1, "height": 2.5, "color": 0x667eea, "position": [0,0,0]},
            {"text": "triangle", "shape": "cone", "size": 1, "radius": 1, "height": 2, "color": 0x667eea, "position": [0,0,0]},
            {"text": "pyramid", "shape": "cone", "size": 1.5, "radius": 1.5, "height": 3, "color": 0x667eea, "position": [0,0,0]},
            
            # Torus
            {"text": "torus", "shape": "torus", "size": 1, "radius": 1, "height": 2, "color": 0x667eea, "position": [0,0,0]},
            {"text": "donut", "shape": "torus", "size": 1.2, "radius": 1.2, "height": 2, "color": 0x667eea, "position": [0,0,0]},
            {"text": "ring", "shape": "torus", "size": 0.8, "radius": 0.8, "height": 2, "color": 0x667eea, "position": [0,0,0]},
        ]
        
        self.training_data = default_data
        self.train_models()
    
    def train_models(self):
        """Train all ML models on current training data"""
        if len(self.training_data) < 5:
            print("Not enough training data")
            return
        
        # Prepare data
        texts = [d["text"] for d in self.training_data]
        shapes = [d["shape"] for d in self.training_data]
        sizes = [d["size"] for d in self.training_data]
        radii = [d["radius"] for d in self.training_data]
        heights = [d["height"] for d in self.training_data]
        
        # Fit vectorizer
        X = self.vectorizer.fit_transform(texts).toarray()
        
        # Train classifiers
        self.shape_classifier.fit(X, shapes)
        self.size_predictor.fit(X, sizes)
        self.radius_predictor.fit(X, radii)
        self.height_predictor.fit(X, heights)
        
        # Train position clusterer
        positions = np.array([d["position"] for d in self.training_data])
        if len(positions) > 0:
            self.position_clusterer.fit(positions)
        
        self.trained = True
        print(f"[OK] Models trained on {len(self.training_data)} examples")
    
    def predict(self, text):
        """Predict shape parameters from text"""
        if not self.trained:
            # Fallback to rule-based
            return self.rule_based_parse(text)
        
        # Vectorize text
        X = self.vectorizer.transform([text]).toarray()
        
        # Predict
        shape = self.shape_classifier.predict(X)[0]
        shape_proba = self.shape_classifier.predict_proba(X)[0]
        confidence = float(max(shape_proba))
        
        size = float(self.size_predictor.predict(X)[0])
        radius = float(self.radius_predictor.predict(X)[0])
        height = float(self.height_predictor.predict(X)[0])
        
        # Find similar examples for color
        color = self.find_similar_color(text)
        
        return {
            "shape": shape,
            "size": max(0.1, size),  # Ensure positive
            "radius": max(0.1, radius),
            "height": max(0.1, height),
            "color": color,
            "position": {"x": 0, "y": 0, "z": 0},
            "confidence": confidence
        }
    
    def find_similar_color(self, text):
        """Find color from similar examples"""
        text_lower = text.lower()
        
        # Check for explicit color words
        color_map = {
            'red': 0xff4444, 'blue': 0x4444ff, 'green': 0x44ff44,
            'yellow': 0xffff44, 'purple': 0xff44ff, 'orange': 0xff8844,
            'cyan': 0x44ffff, 'white': 0xffffff, 'black': 0x222222,
            'pink': 0xff88cc, 'brown': 0x8b4513, 'gray': 0x888888,
            'grey': 0x888888
        }
        
        for color_name, hex_value in color_map.items():
            if color_name in text_lower:
                return hex_value
        
        return 0x667eea  # Default purple
    
    def rule_based_parse(self, text):
        """Fallback rule-based parsing"""
        text_lower = text.lower()
        
        # Detect shape
        if any(word in text_lower for word in ['sphere', 'ball', 'orb', 'globe']):
            shape = 'sphere'
        elif any(word in text_lower for word in ['cube', 'box', 'block', 'square']):
            shape = 'cube'
        elif any(word in text_lower for word in ['cylinder', 'tube', 'pipe', 'column']):
            shape = 'cylinder'
        elif any(word in text_lower for word in ['cone', 'pyramid', 'triangle']):
            shape = 'cone'
        elif any(word in text_lower for word in ['torus', 'donut', 'ring']):
            shape = 'torus'
        else:
            shape = 'sphere'  # Default
        
        # Detect size
        if any(word in text_lower for word in ['large', 'big', 'huge']):
            size = 2.0
        elif any(word in text_lower for word in ['small', 'tiny', 'little']):
            size = 0.5
        else:
            size = 1.0
        
        return {
            "shape": shape,
            "size": size,
            "radius": size,
            "height": 2.5 if shape in ['cylinder', 'cone'] else 2.0,
            "color": self.find_similar_color(text),
            "position": {"x": 0, "y": 0, "z": 0},
            "confidence": 0.7
        }
    
    def save_training_data(self):
        """Save training data to file"""
        filepath = "training_data.json"
        with open(filepath, 'w') as f:
            json.dump(self.training_data, f, indent=2)
        print(f"[OK] Saved {len(self.training_data)} training examples")
    
    def load_training_data(self):
        """Load training data from file"""
        filepath = "training_data.json"
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.training_data = json.load(f)
            if len(self.training_data) >= 5:
                self.train_models()
                print(f"[OK] Loaded {len(self.training_data)} training examples")

# Initialize model
model = TextToCADModel()

# ==========================
# MULTI-OBJECT PARSER
# ==========================

class MultiObjectParser:
    def __init__(self, ml_model):
        self.model = ml_model
    
    def parse(self, text):
        """Parse text and detect multiple objects"""
        text_lower = text.lower()
        objects = []
        
        # Check for multiple objects
        if self.is_multi_object(text_lower):
            objects = self.extract_multiple_objects(text_lower)
        else:
            # Single object
            obj = self.model.predict(text)
            objects = [obj]
        
        return objects
    
    def is_multi_object(self, text):
        """Check if text describes multiple objects"""
        # Keywords that indicate multiple objects
        multi_indicators = [
            r'\d+\s+(spheres|cubes|cylinders|cones)', # "3 cubes"
            r'and\s+(?:a|an)', # "sphere and cube"
            r'with\s+(?:a|an|\d+)', # "table with legs"
            r'stack', 'multiple', 'several',
            r'above', r'below', r'next to', r'on top'
        ]
        
        for pattern in multi_indicators:
            if re.search(pattern, text):
                return True
        return False
    
    def extract_multiple_objects(self, text):
        """Extract multiple objects from text"""
        objects = []
        
        # Pattern 1: Explicit "and" separator
        if ' and ' in text:
            parts = text.split(' and ')
            for i, part in enumerate(parts):
                obj = self.model.predict(part.strip())
                obj['position'] = {"x": i * 2, "y": 0, "z": 0}  # Spread out
                objects.append(obj)
            return objects
        
        # Pattern 2: Number of objects (e.g., "3 cubes")
        quantity_match = re.search(r'(\d+)\s+(sphere|cube|cylinder|cone|torus|ball|box|tube)s?', text)
        if quantity_match:
            count = int(quantity_match.group(1))
            shape_text = quantity_match.group(2)
            
            for i in range(min(count, 10)):  # Max 10 objects
                obj = self.model.predict(shape_text)
                # Arrange in a row
                obj['position'] = {"x": i * 2 - count, "y": 0, "z": 0}
                objects.append(obj)
            return objects
        
        # Pattern 3: Composite objects (e.g.,"house")
        composite_shapes = {
            'house': [
                ('cube walls', {"x": 0, "y": 0, "z": 0}, 3.0),  # walls
                ('cone roof', {"x": 0, "y": 2, "z": 0}, 1.5),  # roof
            ],
            'table': [
                ('cube top', {"x": 0, "y": 2, "z": 0}, 1.0),  # table top
                ('cylinder leg', {"x": -1.5, "y": 0, "z": -1.5}, 0.3),  # legs
                ('cylinder leg', {"x": 1.5, "y": 0, "z": -1.5}, 0.3),
                ('cylinder leg', {"x": -1.5, "y": 0, "z": 1.5}, 0.3),
                ('cylinder leg', {"x": 1.5, "y": 0, "z": 1.5}, 0.3),
            ],
            'snowman': [
                ('large sphere', {"x": 0, "y": 0, "z": 0}, 2.0),  # body
                ('sphere', {"x": 0, "y": 2.5, "z": 0}, 1.5),  # torso
                ('small sphere', {"x": 0, "y": 4.2, "z": 0}, 1.0),  # head
            ],
        }
        
        for composite_name, parts in composite_shapes.items():
            if composite_name in text:
                for part_text, position, size_mult in parts:
                    obj = self.model.predict(part_text)
                    obj['position'] = position
                    obj['size'] *= size_mult
                    obj['radius'] *= size_mult
                    objects.append(obj)
                return objects
        
        # Pattern 4: Stacking (e.g., "stack 3 cubes")
        stack_match = re.search(r'stack\s+(\d+)\s+(\w+)', text)
        if stack_match:
            count = int(stack_match.group(1))
            shape_text = stack_match.group(2)
            
            y_offset = 0
            for i in range(min(count, 10)):
                obj = self.model.predict(shape_text)
                obj['position'] = {"x": 0, "y": y_offset, "z": 0}
                y_offset += obj['size'] * 2  # Stack vertically
                objects.append(obj)
            return objects
        
        # Fallback: single object
        obj = self.model.predict(text)
        objects = [obj]
        
        return objects

# Initialize parser
parser = MultiObjectParser(model)

# ==========================
# API ENDPOINTS
# ==========================

@app.route('/parse-text', methods=['POST'])
def parse_text():
    """Main endpoint for text to CAD conversion"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Parse into objects
        objects = parser.parse(text)
        
        # Save interaction for learning
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "input": text,
            "output": objects
        }
        
        # Could save this and retrain periodically
        
        response = {
            "objects": objects,
            "count": len(objects),
            "interpretation": f"Generated {len(objects)} object(s)",
            "ml_powered": model.trained
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "models_trained": model.trained,
        "training_examples": len(model.training_data)
    })

@app.route('/retrain', methods=['POST'])
def retrain():
    """Retrain models with new data"""
    try:
        data = request.json
        new_example = data.get('example')
        
        if new_example:
            model.training_data.append(new_example)
            model.train_models()
            model.save_training_data()
        
        return jsonify({
            "status": "retrained",
            "total_examples": len(model.training_data)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("[START] AI-Powered Text-to-CAD Backend...")
    print(f"[OK] ML Models: Random Forest, Linear Regression, K-Means")
    print(f"[OK] Training Examples: {len(model.training_data)}")
    print(f"[OK] Multi-Object Support: Enabled")
    print("\n[SERVER] Running on http://localhost:5000")
    print("[API] Endpoints:")
    print("  POST /parse-text - Convert text to CAD objects")
    print("  GET  /health     - Check server status")
    print("  POST /retrain    - Add training data\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
