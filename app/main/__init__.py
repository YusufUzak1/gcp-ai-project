# app/main/__init__.py

from flask import Blueprint

# 'main' adında bir Blueprint (modül) oluşturuyoruz.
# Rotalarımızı (routes.py içinde) bu 'main_bp' değişkenine bağlayacağız.
main_bp = Blueprint('main', __name__)

# ÖNEMLİ: Bu import işlemi, 'main_bp' oluşturulduktan SONRA yapılmalıdır.
# Bu sayede 'routes.py' dosyası 'main_bp' değişkenini bulabilir ve kullanabilir.
from . import routes