"""
W-CERT Extensions
Centralised initialisation of Flask extensions.
"""

from flask_cors import CORS
from flask_jwt_extended import JWTManager

cors = CORS()
jwt = JWTManager()
