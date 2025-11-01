# app/repositories/journal_repo.py
import datetime
from app import db  # app/__init__.py dosyasında oluşturduğumuz global 'db' istemcisi
from google.cloud import firestore

"""
DEPO (REPOSITORY) KATMANI

Bu dosyanın tek sorumluluğu Firestore veritabanı ile konuşmaktır.
- Servis (Service) katmanından gelen veriyi veritabanına kaydeder.
- Controller (Routes) katmanının ihtiyacı olan veriyi veritabanından okur.
- AI analizi veya web istekleri (request/session) hakkında hiçbir şey bilmez.
"""

def save_entry(entry_data):
    """
    Verilen günlük girdisi verisini Firestore'a kaydeder.
    
    Args:
        entry_data (dict): Kaydedilecek veriyi içeren bir sözlük.
                           (Bu, 'journal_service' tarafından hazırlanıp gönderilecek)
                           Örnek: {'userId': '...', 'raw_text': '...', 'analysis': {...}}
    
    Returns:
        str: Oluşturulan yeni belgenin (document) kimliği (ID).
    """
    try:
        # Veriyi kopyalıyoruz (iyi bir pratiktir)
        data_to_save = entry_data.copy()
        
        # dashboard.html şablonunuzda 'e.createdAt' veya 'e.created_at' kullandığınızı gördüm.
        # Bu yüzden, veritabanına 'timestamp' yerine 'created_at' adıyla
        # o anın UTC zaman damgasını ekliyoruz.
        data_to_save['created_at'] = datetime.datetime.now(datetime.timezone.utc)
        
        # 'journal_entries' koleksiyonuna yeni bir belge ekle
        collection_ref = db.collection('journal_entries')
        update_time, doc_ref = collection_ref.add(data_to_save)
        
        print(f"Başarıyla Firestore'a kaydedildi, Belge ID: {doc_ref.id}")
        return doc_ref.id
        
    except Exception as e:
        print(f"Firestore kaydı başarısız: {e}")
        return None

def get_entries_by_user(user_id, limit=20):
    """
    Belirli bir kullanıcı kimliğine (user_id) ait son günlük girdilerini
    Firestore'dan çeker.
    
    Args:
        user_id (str): Girdileri getirilecek kullanıcının kimliği.
        limit (int): Kaç adet girdi çekileceği (varsayılan 20).
    
    Returns:
        list: Her biri bir günlük girdisi olan sözlük (dict) listesi.
    """
    try:
        entries_ref = db.collection('journal_entries')
        
        # --- BU, PROJEMİZİN EN KRİTİK GÜVENLİK KODUDUR ---
        # Sadece 'userId' alanı bizim 'user_id'mizle eşleşen belgeleri çek.
        # Ve bunları 'created_at' alanına göre tersten (en yeni üste) sırala.
        query = (
            entries_ref
            .where('userId', '==', user_id)
            .order_by('created_at', direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        
        docs = query.stream()
        
        entries = []
        for doc in docs:
            entry_data = doc.to_dict()
            entry_data['id'] = doc.id  # Belge ID'sini de ekleyelim
            entries.append(entry_data)
            
        return entries
        
    except Exception as e:
        print(f"Firestore okuma hatası: {e}")
        # --- ÖNEMLİ: İNDEKS HATASI BEKLENTİSİ ---
        # Eğer hata "INVALID_ARGUMENT: The query requires an index..."
        # şeklinde bir mesaj içeriyorsa, bu normaldir.
        # Firestore'un bu özel sorgu (hem 'where' hem 'order_by') için 
        # bir 'bileşik indeks' (composite index) oluşturmasına ihtiyacımız var.
        # Hata mesajı, indeksi oluşturmak için gereken URL'i bize verecektir.
        return []