# app/__init__.py (DÜZELTİLMİŞ VERSİYON)
import os
from flask import Flask
from google.cloud import firestore
from google.cloud import language_v2 as language
import firebase_admin
from firebase_admin import credentials, auth

# --- 1. Servis İstemcilerini 'None' Olarak Tanımla ---
# İstemcileri global alanda oluşturmuyoruz, sadece yerlerini ayırıyoruz.
# Bunlar, 'create_app' içinde başlatıldıktan sonra 'routes.py' gibi
# diğer dosyalardan import edilebilecek.
db = None
lang_client = None
firebase_app = None

def create_app():
    """
    Application Factory: Flask uygulamasını oluşturan ve yapılandıran ana fonksiyon.
    """
    # Global anahtar kelimesiyle, bu fonksiyonun içindeki db, lang_client 
    # ve firebase_app'in, yukarıda tanımladığımız global değişkenler 
    # olduğunu belirtiyoruz.
    global db, lang_client, firebase_app

    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = 'BURAYA_COK_GUVENLI_RASTGELE_BIR_ANAHTAR_GELECEK'

    # --- 2. GCP & Firebase Servislerinin Başlatılması ---
    
    # ADIM 2.A: ÖNCE Kimlik Bilgilerini Ayarla
    # Local'de çalışıyorsak 'service_account.json' dosyasını ara
    if not os.getenv('GAE_ENV', '').startswith('standard'):
        json_path = os.path.join(os.path.dirname(__file__), '..', 'service_account.json')
        if os.path.exists(json_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = json_path
        else:
            # Bu bir HATA DEĞİL, UYARIDIR. 
            # Sunucunun çalışmasını engellemez.
            print("UYARI: 'service_account.json' dosyası bulunamadı.")
            print("GCP Servislerine (Firestore, NLP) bağlanılamayacak.")
    
    # ADIM 2.B: SONRA İstemcileri Başlat
    # Artık 'GOOGLE_APPLICATION_CREDENTIALS' ayarlandı (veya eksikse uyarı verildi).
    try:
        if not db:
            db = firestore.Client()
        if not lang_client:
            lang_client = language.LanguageServiceClient()
    except Exception as e:
        print(f"GCP İstemcileri (db, lang_client) başlatılamadı: {e}")
        print("Eğer 'service_account.json' dosyası eksikse bu beklenen bir durumdur.")

    # ADIM 2.C: Firebase Admin SDK'yı Başlat
    if not firebase_app:
        try:
            cred = credentials.ApplicationDefault()
            firebase_app = firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"Firebase Admin SDK başlatılamadı: {e}")

    # --- 3. Blueprint (Modül/Rotalar) Kaydı ---
    from .main import main_bp
    app.register_blueprint(main_bp)

    return app