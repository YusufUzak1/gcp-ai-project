# main.py
import os
from app import create_app

# Application Factory'yi (app/__init__.py içindeki) çağırarak 
# Flask uygulama nesnesini oluşturuyoruz.
app = create_app()

if __name__ == '__main__':
    # Bu blok, sadece dosyayı doğrudan 'python main.py' komutuyla 
    # çalıştırdığımızda (yani local'de test ederken) tetiklenir.
    # Cloud Run gibi üretim ortamları bu bloğu çalıştırmaz, 
    # bunun yerine 'gunicorn' gibi bir sunucu kullanır.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))