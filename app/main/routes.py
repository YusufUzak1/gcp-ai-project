# app/main/routes.py (GÜNCELLENMİŞ SON SÜRÜM)

from . import main_bp
from flask import (
    render_template, 
    redirect, 
    url_for, 
    flash, 
    session, 
    request,
    g
)
from functools import wraps

# --- YENİ İMPORTLAR (SERVİS VE DEPO KATMANLARI) ---
# İş mantığı (orkestra şefi) için servis katmanını import ediyoruz
from app.services import create_new_entry
# Veri okuma (girdileri listeleme) için depo katmanını import ediyoruz
from app.repositories import get_entries_by_user

# --- 1. Kullanıcı Oturumunu (Session) Yönetmek ---
# (Bu kısım değişmedi)
@main_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = {'is_authenticated': False}
    else:
        g.user = {'is_authenticated': True, 'id': user_id}

@main_bp.context_processor
def inject_user():
    return dict(current_user=g.user)


# --- 2. 'Giriş Gerekli' Decorator'ı ---
# (Bu kısım değişmedi)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user['is_authenticated']:
            flash('Lütfen devam etmek için giriş yapın.', 'error')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function


# --- 3. Rotalar (Sayfalar) ---

@main_bp.route('/')
def index():
    # (Bu kısım değişmedi)
    if g.user['is_authenticated']:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    # (Bu kısım değişmedi)
    if g.user['is_authenticated']:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Lütfen bir e-posta veya kullanıcı kimliği girin.', 'error')
            return render_template('login.html')
        
        session['user_id'] = email
        session.permanent = True 
        
        flash('Başarıyla giriş yaptınız!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')


@main_bp.route('/logout')
@login_required 
def logout():
    # (Bu kısım değişmedi)
    session.pop('user_id', None)
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('main.login'))


# --- DEĞİŞİKLİK BURADA (DASHBOARD) ---
@main_bp.route('/dashboard')
@login_required 
def dashboard():
    """
    /dashboard sayfası. 
    Kullanıcının ana paneli.
    """
    
    # --- FAZ 3 YER TUTUCU KALDIRILDI ---
    # Artık boş liste ('[]') göndermiyoruz.
    # Doğrudan 'journal_repo.py' dosyasındaki fonksiyonu çağırıyoruz
    # ve sadece bu kullanıcıya ('g.user['id']') ait girdileri çekiyoruz.
    try:
        entries = get_entries_by_user(g.user['id'])
    except Exception as e:
        # Bu, büyük ihtimalle 'Firestore İndeks Hatası'dır.
        print(f"DASHBOARD HATASI: Girdiler çekilemedi: {e}")
        flash('Girdileriniz yüklenirken bir sorun oluştu. Lütfen terminali kontrol edin.', 'error')
        entries = []
    
    return render_template('dashboard.html', entries=entries)


# --- DEĞİŞİKLİK BURADA (NEW ENTRY) ---
@main_bp.route('/new-entry', methods=['POST'])
@login_required 
def new_entry():
    """
    /new-entry adresi. Sadece POST metoduyla çalışır.
    Dashboard'daki formdan gelen yeni girdiyi alır.
    """
    text = request.form.get('text')
    
    if not text:
        flash('Girdi boş olamaz.', 'error')
        return redirect(url_for('main.dashboard'))

    user_id = g.user['id']
    
    # --- FAZ 3 YER TUTUCU KALDIRILDI ---
    # Artık sadece terminale yazdırmıyoruz.
    # 'journal_service.py' dosyasındaki 'orkestra şefi' 
    # fonksiyonumuzu ('create_new_entry') çağırıyoruz.
    # Bu fonksiyon AI analizini ve veritabanı kaydını halledecek.
    try:
        success = create_new_entry(user_id, text)
        
        if success:
            flash('Yeni girdi başarıyla analiz edildi ve kaydedildi!', 'success')
        else:
            flash('Girdiniz kaydedilirken bir sorun oluştu.', 'error')
            
    except Exception as e:
        print(f"NEW_ENTRY HATASI: Girdi oluşturulamadı: {e}")
        flash('Girdiniz oluşturulurken beklenmedik bir hata oluştu.', 'error')
    
    return redirect(url_for('main.dashboard'))