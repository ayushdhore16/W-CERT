"""
W-CERT Application Factory
Creates and configures the Flask application.
"""

import os
from flask import Flask, jsonify
from .config import config_by_name
from .extensions import cors, jwt


def create_app(config_name=None):
    """Create the Flask application using the app factory pattern."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Ensure upload directory exists
    upload_path = os.path.join(app.root_path, '..', app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_path, exist_ok=True)

    # ── Initialise extensions ──────────────────────────────────
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    jwt.init_app(app)

    # ── JWT error handlers ─────────────────────────────────────
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired", "code": "TOKEN_EXPIRED"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token", "code": "INVALID_TOKEN"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    # ── Register blueprints ────────────────────────────────────
    from .api.auth_routes import auth_bp
    from .api.incident_routes import incident_bp
    from .api.evidence_routes import evidence_bp
    from .api.dashboard_routes import dashboard_bp
    from .api.escalation_routes import escalation_bp
    from .api.admin_routes import admin_bp
    from .api.status_routes import status_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(incident_bp, url_prefix='/api/incidents')
    app.register_blueprint(evidence_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(escalation_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(status_bp, url_prefix='/api')

    # ── Health check ───────────────────────────────────────────
    @app.route('/')
    def health_check():
        return jsonify({
            "service": "W-CERT Backend API",
            "status": "online",
            "version": "1.0.0"
        }), 200

    # ── Global error handlers ──────────────────────────────────
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app
