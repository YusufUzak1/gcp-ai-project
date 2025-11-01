# app/services/nlp_service.py (NİHAİ DÜZELTİLMİŞ SÜRÜM)

from app import lang_client
from google.cloud import language_v2
import traceback

"""
SERVİS (NLP) KATMANI
"""

def analyze_text(raw_text):
    """
    Verilen bir metnin duygu (sentiment) ve varlık (entity) analizini yapar.
    """
    try:
        # 1. API'ye göndereceğimiz 'Document' nesnesini hazırla
        document = language_v2.types.Document(
            content=raw_text,
            type_=language_v2.types.Document.Type.PLAIN_TEXT,
        )
        
        # 2. API'den hem duygu (sentiment) hem de varlık (entity) analizi istiyoruz
        # (Bu blok artık DOĞRU)
        features = language_v2.types.AnnotateTextRequest.Features(
            extract_document_sentiment=True,
            extract_entities=True
        )

        # 3. API çağrısını yap
        response = lang_client.annotate_text(
            document=document,
            features=features,
            encoding_type=language_v2.EncodingType.UTF8
        )

        # 4. Duygu (Sentiment) Sonuçlarını İşle
        sentiment = response.document_sentiment
        sentiment_data = {
            'score': sentiment.score,
            'magnitude': sentiment.magnitude
        }

        # 5. Varlık (Entity) Sonuçlarını İşle
        entities_data = []
        for entity in response.entities:
            
            # --- BURASI DÜZELTİLDİ (HATALI KOD YERİNE DOĞRU KOD) ---
            # 'salience' (önem) alanı her varlıkta (entity) bulunmayabilir.
            # 'getattr' kullanarak, eğer 'salience' alanı yoksa
            # varsayılan olarak 0.0 değerini atıyoruz.
            salience_score = getattr(entity, 'salience', 0.0)
            
            entities_data.append({
                'name': entity.name,
                'type': entity.type_.name,
                'salience': salience_score # Güvenli değişkeni kullan
            })

        # 6. Sonucu birleştir ve döndür
        analysis_result = {
            'language_code': response.language_code,
            'sentiment': sentiment_data,
            'entities': entities_data
        }
        
        print(f"NLP Analizi başarılı. Dil: {response.language_code}, Duygu: {sentiment.score}")
        return analysis_result

    except Exception as e:
        print(f"Cloud Natural Language API hatası: {e}")
        traceback.print_exc() 
        
        return {
            'language_code': 'und', 
            'sentiment': {'score': 0, 'magnitude': 0},
            'entities': []
        }