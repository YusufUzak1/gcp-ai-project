# app/services/journal_service.py

# Az önce oluşturduğumuz diğer katmanlardan fonksiyonları import ediyoruz
from app.services import analyze_text
from app.repositories import save_entry

"""
SERVİS (İŞ MANTIĞI) KATMANI

Bu dosya, projenin "beynidir". 
- Controller (routes.py) katmanından emirleri (örn: "yeni girdi oluştur") alır.
- Diğer servisleri (örn: nlp_service) ve depoları (örn: journal_repo)
  koordine ederek iş akışını yönetir.
- Web istekleri (request) veya veritabanı sorgularının (query) 
  detaylarını bilmez. Sadece "orkestrasyon" yapar.
"""

def create_new_entry(user_id, raw_text):
    """
    Yeni bir günlük girdisi oluşturma işleminin tamamını yönetir.
    1. Metni analiz eder.
    2. Veritabanına kaydedilecek son veriyi hazırlar.
    3. Veritabanına kaydeder.
    
    Args:
        user_id (str): Girdinin sahibi olan kullanıcının kimliği.
        raw_text (str): Kullanıcının girdiği ham metin.
        
    Returns:
        bool: İşlem başarılıysa True, değilse False.
    """
    print(f"JournalService: Yeni girdi oluşturuluyor. Kullanıcı: {user_id}")
    
    # 1. Adım: AI Servisini Çağır (NLP Analizi)
    # 'nlp_service.py' dosyasındaki fonksiyonu çağırıyoruz.
    print("JournalService: Metin analizi için nlp_service çağrılıyor...")
    analysis_data = analyze_text(raw_text)
    
    # 2. Adım: Veritabanı Modelini Hazırla
    # 'journal_repo.py' dosyasındaki 'save_entry' fonksiyonunun 
    # beklediği sözlük (dict) formatını hazırlıyoruz.
    entry_data_to_save = {
        'userId': user_id,
        'raw_text': raw_text,
        'analysis': analysis_data  # AI'dan gelen analiz sonucu
    }
    
    # 3. Adım: Depo (Repository) Katmanını Çağır (Kaydet)
    # 'journal_repo.py' dosyasındaki fonksiyonu çağırıyoruz.
    print("JournalService: Kayıt için journal_repo çağrılıyor...")
    saved_doc_id = save_entry(entry_data_to_save)
    
    if saved_doc_id:
        print(f"JournalService: İşlem başarılı. Yeni Belge ID: {saved_doc_id}")
        return True
    else:
        print("JournalService: İşlem başarısız (kayıt yapılamadı).")
        return False