import os
import datetime
import uuid # Resimlere benzersiz isimler vermek için
from flask import Flask, render_template, request, redirect, url_for, flash

# Google Cloud Servislerini içe aktar
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage
from google.cloud import vision

# --- Servis Bağlantıları ---

# Cloud Run'da çalışırken, Google kimlik bilgilerini
# otomatik olarak (Adım 1.4'te verdiğimiz izinlerle) alır.
try:
    firebase_admin.initialize_app()
except ValueError:
    pass # Zaten başlatılmışsa hata verme

# 1. Firestore Veritabanı (Sonuçları saklamak için)
db = firestore.client()
results_collection = db.collection('ai_results')

# 2. Cloud Storage (Resimleri yüklemek için)
storage_client = storage.Client()
# TODO: BURAYI DEĞİŞTİRİN! Adım 1.2'de oluşturduğunuz benzersiz kova adını yazın.
BUCKET_NAME = "BURAYA_KOVA_ADINIZI_YAZIN" # Örn: "benim-devops-projem-12345-uploads"

# 3. Cloud Vision (Yapay Zeka Analizi için)
vision_client = vision.ImageAnnotatorClient()

# ------------------------------

app = Flask(__name__)
# Gizli anahtar, 'flash' mesajları (örn: "Hata: Sadece resim yükleyin") için gereklidir
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_super_secret_key_for_dev")

# İzin verilen dosya uzantıları
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """
    Ana sayfayı yükler ve veritabanındaki TÜM sonuçları çeker.
    Bu, sizin index.html'inizdeki 'results' değişkenini doldurur.
    """
    
    # Sonuçları veritabanından al, 'timestamp' (zaman damgası) alanına göre
    # en yeniden en eskiye (DESCENDING) doğru sırala.
    results_stream = results_collection.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
    
    # Gelen veriyi HTML'in anlayacağı bir listeye dönüştür
    results_list = []
    for result in results_stream:
        results_list.append(result.to_dict())

    # index.html'i aç ve 'results' değişkenini bu listeyle doldur
    return render_template('index.html', results=results_list)

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Formdan gelen resmi alır, depolar, analiz eder ve veritabanına kaydeder.
    Bu, sizin formunuzdaki action="/analyze" kısmını yakalar.
    """
    
    # 1. Dosyayı Formdan Al
    if 'image_file' not in request.files:
        flash("Formda 'image_file' bölümü bulunamadı.")
        return redirect(url_for('index'))
    
    file = request.files['image_file']
    
    if file.filename == '':
        flash("Resim seçilmedi.")
        return redirect(url_for('index'))

    # 2. Dosya Tipini Kontrol Et
    if not file or not allowed_file(file.filename):
        flash("Hata: Sadece .png, .jpg, .jpeg formatında resim yükleyebilirsiniz.")
        return redirect(url_for('index'))

    try:
        # 3. Dosyayı Cloud Storage'a Yükle
        bucket = storage_client.bucket(BUCKET_NAME)
        # Dosya adının çakışmaması için benzersiz bir isim oluştur (örn: 123e4567...jpg)
        unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        blob = bucket.blob(unique_filename)
        
        # Dosyayı yükle
        blob.upload_from_file(file.stream, content_type=file.content_type)
        
        # Resmin genel URL'sini al (Adım 1.3'te 'allUsers' izni verdiğimiz için çalışır)
        image_public_url = blob.public_url

        # 4. Resmi Cloud Vision API ile Analiz Et
        # Yapay zekaya resmin URL'sini ver
        image = vision.Image(source=vision.ImageSource(image_uri=image_public_url))
        
        # "Label Detection" (Etiket Tespiti) özelliğini kullan
        response = vision_client.label_detection(image=image)
        labels_annotations = response.label_annotations
        
        # Gelen etiketleri (örn: 'Kedi', 'Memeli'...) bir listeye ayıkla
        labels_list = [label.description for label in labels_annotations]

        # 5. Sonuçları Firestore'a Kaydet
        data_to_save = {
            'image_url': image_public_url,
            'labels': labels_list,
            'timestamp': datetime.datetime.now(datetime.timezone.utc)
        }
        results_collection.add(data_to_save)

    except Exception as e:
        # Bir hata olursa (örn: Kova adı yanlışsa, Vision API izni yoksa)
        flash(f"Bir hata oluştu: {e}")
        return redirect(url_for('index'))

    # 6. Kullanıcıyı ana sayfaya geri yönlendir (yenilenen galeriyi görecek)
    return redirect(url_for('index'))

# Dockerfile'ımızın Gunicorn ile kullanacağı kısım
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)