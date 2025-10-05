from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session, make_response
from utils.database import (get_db_connection, create_stok_hareketi, stok_giris, 
                            stok_cikis, stok_transfer, get_all_locations_for_product,
                            get_product_stock_summary, get_urun_rezervasyon_notu)
from utils.excel_processor import ExcelProcessor, DatabaseImporter
from utils.auth import UserManager, login_required, admin_required, get_current_user, is_admin, can_access_page
import os
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

# Initialize UserManager
user_manager = None

def init_user_manager():
    """Initialize user manager with database connection"""
    global user_manager
    if user_manager is None:
        from utils.database import DatabaseManager
        db_manager = DatabaseManager()
        user_manager = UserManager(db_manager)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Kullanıcı giriş sayfası"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Kullanıcı adı ve şifre gereklidir.', 'error')
            return render_template('login.html')
        
        init_user_manager()
        user = user_manager.authenticate_user(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['kullanici_adi']
            session['user_role'] = user['rol']
            
            flash(f'Hoş geldiniz, {username}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Geçersiz kullanıcı adı veya şifre.', 'error')
    
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    """Kullanıcı çıkış"""
    username = session.get('username', 'Kullanıcı')
    session.clear()
    flash(f'Güle güle, {username}!', 'success')
    return redirect(url_for('main.login'))

@main_bp.route('/user-management')
@admin_required
def user_management():
    """Kullanıcı yönetimi sayfası (sadece admin)"""
    init_user_manager()
    users = user_manager.get_all_users()
    active_users = len([u for u in users if u['aktif']])
    
    return render_template('user_management.html', 
                         users=users, 
                         active_users=active_users)

@main_bp.route('/add-user', methods=['POST'])
@admin_required
def add_user():
    """Yeni kullanıcı ekleme"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'user')
    
    if not username or not password:
        flash('Kullanıcı adı ve şifre gereklidir.', 'error')
        return redirect(url_for('main.user_management'))
    
    if len(password) < 4:
        flash('Şifre en az 4 karakter olmalıdır.', 'error')
        return redirect(url_for('main.user_management'))
    
    init_user_manager()
    if user_manager.create_user(username, password, role):
        flash(f'Kullanıcı {username} başarıyla eklendi.', 'success')
    else:
        flash('Kullanıcı eklenirken hata oluştu. Bu kullanıcı adı zaten kullanımda olabilir.', 'error')
    
    return redirect(url_for('main.user_management'))

@main_bp.route('/toggle-user-status/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Kullanıcı durumunu aktif/pasif yap"""
    init_user_manager()
    user_manager.toggle_user_status(user_id)
    flash('Kullanıcı durumu güncellendi.', 'success')
    return redirect(url_for('main.user_management'))

@main_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Kullanıcı silme"""
    init_user_manager()
    user_manager.delete_user(user_id)
    flash('Kullanıcı başarıyla silindi.', 'success')
    return redirect(url_for('main.user_management'))

@main_bp.route('/welcome')
def welcome():
    """Hoş geldin sayfası - Rigel logosu ile"""
    return render_template('welcome.html')

@main_bp.route('/')
def dashboard():
    """Ana sayfa - Dashboard"""
    # Kullanıcı giriş yapmış mı kontrol et
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    # Kullanıcı rolüne göre farklı görünüm
    if not is_admin():
        # Normal kullanıcılar sadece stok raporuna yönlendirilir
        return redirect(url_for('main.stock_report'))
    try:
        db = get_db_connection()
        
        # İstatistikleri hesapla
        stats = {}
        
        # Toplam ürün çeşidi
        result = db.execute('SELECT COUNT(DISTINCT urun_kodu) as count FROM stoklar').fetchone()
        stats['total_products'] = result['count'] if result else 0
        
        # Toplam adet
        result = db.execute('SELECT SUM(adet) as total FROM stoklar').fetchone()
        stats['total_quantity'] = result['total'] if result and result['total'] else 0
        
        # Toplam ağırlık
        result = db.execute('SELECT SUM(toplam_kg) as total FROM stoklar').fetchone()
        stats['total_weight'] = result['total'] if result and result['total'] else 0
        
        # Konum sayısı
        result = db.execute('SELECT COUNT(DISTINCT konum) as count FROM stoklar WHERE konum IS NOT NULL').fetchone()
        stats['total_locations'] = result['count'] if result else 0
        
        # Son hareketler (son 10)
        recent_movements = db.execute('''
            SELECT DISTINCT h.id, h.urun_kodu, h.hareket_tipi, h.miktar, 
                   h.onceki_miktar, h.yeni_miktar, h.konum, h.aciklama, 
                   h.kullanici, h.tarih,
                   (SELECT s2.urun_adi FROM stoklar s2 WHERE s2.urun_kodu = h.urun_kodu LIMIT 1) as urun_adi
            FROM stok_hareketleri h
            ORDER BY h.tarih DESC 
            LIMIT 10
        ''').fetchall()
        
        # Kritik stok uyarıları (her ürün için özel sınır)
        low_stock_items = db.execute('''
            SELECT urun_kodu, urun_adi, konum, adet, kritik_stok_siniri
            FROM stoklar 
            WHERE adet <= kritik_stok_siniri AND adet > 0
            ORDER BY (CAST(adet AS FLOAT) / NULLIF(kritik_stok_siniri, 0)) ASC, adet ASC
            LIMIT 10
        ''').fetchall()
        
        # En çok stok bulunan konumlar
        top_locations = db.execute('''
            SELECT konum, 
                   COUNT(DISTINCT urun_kodu) as urun_cesidi,
                   SUM(adet) as toplam_adet,
                   SUM(toplam_kg) as toplam_agirlik
            FROM stoklar 
            WHERE konum IS NOT NULL AND adet > 0
            GROUP BY konum
            ORDER BY toplam_adet DESC
            LIMIT 8
        ''').fetchall()
        
        # En çok stoku olan ürünler (4 adet)
        top_products = db.execute('''
            SELECT urun_kodu, urun_adi,
                   SUM(adet) as toplam_adet,
                   COUNT(DISTINCT konum) as konum_sayisi,
                   SUM(toplam_kg) as toplam_agirlik
            FROM stoklar 
            WHERE adet > 0
            GROUP BY urun_kodu, urun_adi
            ORDER BY toplam_adet DESC
            LIMIT 4
        ''').fetchall()
        
        # Stoğu azalan ürünler (kritik stok sınırına yakın olanlar)
        low_stock_products = db.execute('''
            SELECT urun_kodu, urun_adi, konum, adet, kritik_stok_siniri,
                   CASE 
                       WHEN kritik_stok_siniri > 0 THEN ROUND((CAST(adet AS FLOAT) / kritik_stok_siniri) * 100, 1)
                       ELSE 100.0
                   END as stok_yuzde
            FROM stoklar 
            WHERE adet > 0 AND adet <= (kritik_stok_siniri * 1.5)
            ORDER BY stok_yuzde ASC, adet ASC
            LIMIT 8
        ''').fetchall()
        
        return render_template('index.html', 
                             stats=stats, 
                             recent_movements=recent_movements,
                             low_stock_items=low_stock_items,
                             top_locations=top_locations,
                             top_products=top_products,
                             low_stock_products=low_stock_products)
    
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        flash(f'Dashboard yüklenirken hata oluştu: {str(e)}', 'error')
        return render_template('index.html', stats={}, recent_movements=[], 
                             low_stock_items=[], top_locations=[], top_products=[], low_stock_products=[])

@main_bp.route('/stock-list')
@admin_required
def stock_list():
    """Stok listesi sayfası"""
    try:
        db = get_db_connection()
        page = request.args.get('page', 1, type=int)
        per_page = 50
        offset = (page - 1) * per_page
        
        # Arama ve filtreleme
        search = request.args.get('search', '').strip()
        location = request.args.get('location', '').strip()
        color = request.args.get('color', '').strip()
        sistem_seri = request.args.get('sistem_seri', '').strip()  # Add sistem_seri filter
        
        # Sıralama parametreleri
        sort_by = request.args.get('sort_by', 'urun_kodu')  # Varsayılan sıralama
        sort_order = request.args.get('sort_order', 'asc')  # asc veya desc
        
        # Geçerli sıralama kolonları
        valid_sort_columns = {
            'urun_kodu': 'urun_kodu',
            'urun_adi': 'urun_adi', 
            'renk': 'renk',
            'sistem_seri': 'sistem_seri',
            'uzunluk': 'uzunluk',
            'mt_kg': 'mt_kg',
            'boy_kg': 'boy_kg',
            'adet': 'adet',
            'toplam_kg': 'toplam_kg',
            'konum': 'konum'
        }
        
        # Sıralama parametrelerini doğrula
        if sort_by not in valid_sort_columns:
            sort_by = 'urun_kodu'
        if sort_order not in ['asc', 'desc']:
            sort_order = 'asc'
        
        # Base query
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append('(urun_kodu LIKE ? OR urun_adi LIKE ?)')
            params.extend([f'%{search}%', f'%{search}%'])
        
        if location:
            where_conditions.append('konum = ?')
            params.append(location)
            
        if color:
            where_conditions.append('renk = ?')
            params.append(color)
            
        # Add sistem_seri filter condition
        if sistem_seri:
            where_conditions.append('sistem_seri LIKE ?')
            params.append(f'%{sistem_seri}%')
        
        where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
        
        # Sıralama kısmını oluştur
        order_clause = f"ORDER BY {valid_sort_columns[sort_by]} {sort_order.upper()}"
        # İkincil sıralama ekle (aynı değerler için)
        if sort_by != 'urun_kodu':
            order_clause += ", urun_kodu ASC"
        
        # Toplam kayıt sayısı
        count_query = f'SELECT COUNT(*) as total FROM stoklar WHERE {where_clause}'
        total = db.execute(count_query, params).fetchone()['total']
        
        # Stok listesi (sadece rezervasyon notu ile)
        query = f'''
            SELECT s.*, s.kritik_stok_siniri
            FROM stoklar s
            WHERE {where_clause}
            {order_clause}
            LIMIT ? OFFSET ?
        '''
        stocks = db.execute(query, params + [per_page, offset]).fetchall()
        
        # Her bir stok kaydı için ürün bazlı rezervasyon notunu al
        stocks_with_reservations = []
        for stock in stocks:
            stock_dict = dict(stock)
            # Ürün bazlı rezervasyon notunu al
            rezervasyon_notu = get_urun_rezervasyon_notu(stock['urun_kodu'], stock['renk'] if stock['renk'] else None)
            stock_dict['rezervasyon_notu'] = rezervasyon_notu
            
            # Rezervasyon olup olmadığını kontrol et
            stock_dict['has_reservations'] = rezervasyon_notu is not None and rezervasyon_notu.strip() != ''
            
            logger.info(f"Stock {stock['urun_kodu']} with color {stock['renk']}: reservation note = '{rezervasyon_notu}'")
            
            stocks_with_reservations.append(stock_dict)
        
        # Filtre seçenekleri
        locations = db.execute('SELECT DISTINCT konum FROM stoklar WHERE konum IS NOT NULL ORDER BY konum').fetchall()
        colors = db.execute('SELECT DISTINCT renk FROM stoklar WHERE renk IS NOT NULL ORDER BY renk').fetchall()
        
        # Sayfalama bilgileri
        has_prev = page > 1
        has_next = offset + per_page < total
        prev_num = page - 1 if has_prev else None
        next_num = page + 1 if has_next else None
        
        return render_template('stock_list.html',
                             stocks=stocks_with_reservations,
                             total=total,
                             page=page,
                             per_page=per_page,
                             has_prev=has_prev,
                             has_next=has_next,
                             prev_num=prev_num,
                             next_num=next_num,
                             locations=locations,
                             colors=colors,
                             search=search,
                             location=location,
                             color=color,
                             sort_by=sort_by,
                             sort_order=sort_order)
    
    except Exception as e:
        logger.error(f"Stock list error: {str(e)}")
        flash(f'Stok listesi yüklenirken hata oluştu: {str(e)}', 'error')
        return render_template('stock_list.html', stocks=[], total=0)

@main_bp.route('/excel-import', methods=['GET', 'POST'])
def excel_import():
    """Excel import sayfası"""
    if request.method == 'GET':
        return render_template('excel_import.html')
    
    try:
        # Dosya kontrolü
        if 'excel_file' not in request.files:
            flash('Dosya seçilmedi', 'error')
            return redirect(request.url)
        
        file = request.files['excel_file']
        if file.filename == '':
            flash('Dosya seçilmedi', 'error')
            return redirect(request.url)
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            flash('Sadece Excel dosyaları (.xlsx, .xls) kabul edilir', 'error')
            return redirect(request.url)
        
        # Dosyayı kaydet
        filename = f"import_{file.filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Excel işleme
        processor = ExcelProcessor()
        data, errors, stats = processor.process_excel_file(filepath, '3')
        
        if data is None or data.empty:
            flash('Excel dosyası işlenemedi veya veri bulunamadı', 'error')
            if errors:
                for error in errors:
                    flash(error, 'error')
            return redirect(request.url)
        
        # Veritabanına import
        db = get_db_connection()
        importer = DatabaseImporter(db)
        result = importer.import_to_database(data)
        
        # Sonuçları göster
        if result['success']:
            flash(f"Import başarılı! {result['imported']} yeni kayıt, {result['updated']} güncelleme", 'success')
            if result['errors'] > 0:
                flash(f"{result['errors']} kayıtta hata oluştu", 'warning')
        else:
            flash(f"Import başarısız: {result['message']}", 'error')
        
        # Geçici dosyayı sil
        try:
            os.remove(filepath)
        except:
            pass
        
        return redirect(url_for('main.dashboard'))
    
    except Exception as e:
        logger.error(f"Excel import error: {str(e)}")
        flash(f'Excel import hatası: {str(e)}', 'error')
        return redirect(request.url)

@main_bp.route('/stock-entry', methods=['GET', 'POST'])
@admin_required
def stock_entry():
    """Stok giriş sayfası"""
    if request.method == 'GET':
        # Mevcut konumları ve renkleri getir
        db = get_db_connection()
        locations = db.execute('SELECT DISTINCT konum FROM stoklar WHERE konum IS NOT NULL ORDER BY konum').fetchall()
        colors = db.execute('SELECT DISTINCT renk FROM stoklar WHERE renk IS NOT NULL ORDER BY renk').fetchall()
        
        # Bugünün tarihini ekle
        from datetime import date
        today = date.today().strftime('%Y-%m-%d')
        
        return render_template('stock_entry.html', locations=locations, colors=colors, today=today)
    
    try:
        # Form verilerini al
        urun_kodu = request.form.get('urun_kodu', '').strip().upper()
        urun_adi = request.form.get('urun_adi', '').strip()
        sistem_seri = request.form.get('sistem_seri', '').strip()
        renk = request.form.get('renk', '').strip()
        uzunluk = int(request.form.get('uzunluk', 0)) if request.form.get('uzunluk') else None
        mt_kg = float(request.form.get('mt_kg', 0)) if request.form.get('mt_kg') else None
        adet = int(request.form.get('adet', 0))
        konum = request.form.get('konum', '').strip()
        islem_tarihi = request.form.get('islem_tarihi', '').strip()
        
        # Validasyon
        if not urun_kodu or not urun_adi:
            flash('Ürün kodu ve ürün adı zorunludur', 'error')
            return redirect(request.url)
        
        if adet <= 0:
            flash('Adet 0\'dan büyük olmalıdır', 'error')
            return redirect(request.url)
        
        if not konum:
            flash('Konum zorunludur', 'error')
            return redirect(request.url)
        
        # Stok giriş işlemini yap
        result = stok_giris(
            urun_kodu=urun_kodu,
            urun_adi=urun_adi,
            renk=renk,
            konum=konum,
            adet=adet,
            mt_kg=mt_kg,
            uzunluk=uzunluk,
            sistem_seri=sistem_seri,
            kullanici='Manuel Giriş',
            islem_tarihi=islem_tarihi
        )
        
        if result['success']:
            flash(f"Şok giriş başarılı: {urun_kodu} - {adet} adet eklendi", 'success')
            return redirect(url_for('main.stock_list'))
        else:
            flash(f'Stok giriş hatası: {result["message"]}', 'error')
            return redirect(request.url)
        
    except ValueError as e:
        flash('Geçersiz sayısal değer girdiniz', 'error')
        return redirect(request.url)
    except Exception as e:
        logger.error(f"Stock entry error: {str(e)}")
        flash(f'Stok giriş hatası: {str(e)}', 'error')
        return redirect(request.url)

@main_bp.route('/stock-add', methods=['GET', 'POST'])
@admin_required
def stock_add():
    """Mevcut stoka ekleme sayfası - stok çıkışı tarzında"""
    if request.method == 'GET':
        # Mevcut ürünler, konumlar ve renkleri getir
        db = get_db_connection()
        products = db.execute('''
            SELECT DISTINCT urun_kodu, urun_adi 
            FROM stoklar 
            ORDER BY urun_kodu
        ''').fetchall()
        
        locations = db.execute('''
            SELECT DISTINCT konum 
            FROM stoklar 
            WHERE konum IS NOT NULL 
            ORDER BY konum
        ''').fetchall()
        
        colors = db.execute('''
            SELECT DISTINCT renk 
            FROM stoklar 
            WHERE renk IS NOT NULL 
            ORDER BY renk
        ''').fetchall()
        
        # Bugünün tarihini ekle
        from datetime import date
        today = date.today().strftime('%Y-%m-%d')
        
        return render_template('stock_add.html', 
                             products=products, 
                             locations=locations, 
                             colors=colors, 
                             today=today)
    
    try:
        # Form verilerini al
        urun_kodu = request.form.get('urun_kodu', '').strip().upper()
        renk = request.form.get('renk', '').strip()
        konum = request.form.get('konum', '').strip()
        adet = int(request.form.get('adet', 0))
        aciklama = request.form.get('aciklama', '').strip()
        islem_tarihi = request.form.get('islem_tarihi', '').strip()
        
        # Validasyon
        if not urun_kodu:
            flash('Ürün kodu zorunludur', 'error')
            return redirect(request.url)
        
        if not konum:
            flash('Konum zorunludur', 'error')
            return redirect(request.url)
        
        if adet <= 0:
            flash('Adet 0\'dan büyük olmalıdır', 'error')
            return redirect(request.url)
        
        # Mevcut ürün bilgilerini al
        db = get_db_connection()
        existing_product = db.execute('''
            SELECT * FROM stoklar 
            WHERE urun_kodu = ? 
            LIMIT 1
        ''', [urun_kodu]).fetchone()
        
        if not existing_product:
            flash(f'Ürün kodu {urun_kodu} bulunamadı. Yeni ürün eklemek için "Yeni Ürün Ekle" sayfasını kullanın.', 'error')
            return redirect(request.url)
        
        # Stok giriş işlemini yap (mevcut ürün bilgileriyle)
        result = stok_giris(
            urun_kodu=urun_kodu,
            urun_adi=existing_product['urun_adi'],
            renk=renk,
            konum=konum,
            adet=adet,
            mt_kg=existing_product['mt_kg'],
            uzunluk=existing_product['uzunluk'],
            sistem_seri=existing_product['sistem_seri'],
            kullanici='Mevcut Stoka Ekleme',
            islem_tarihi=islem_tarihi
        )
        
        if result['success']:
            flash(f"Stok ekleme başarılı: {urun_kodu} - {adet} adet eklendi", 'success')
            return redirect(url_for('main.stock_list'))
        else:
            flash(f'Stok ekleme hatası: {result["message"]}', 'error')
            return redirect(request.url)
        
    except ValueError as e:
        flash('Geçersiz sayısal değer girdiniz', 'error')
        return redirect(request.url)
    except Exception as e:
        logger.error(f"Stock add error: {str(e)}")
        flash(f'Stok ekleme hatası: {str(e)}', 'error')
        return redirect(request.url)

@main_bp.route('/api/check-stock')
def api_check_stock():
    """Stok kontrol API endpoint"""
    try:
        urun_kodu = request.args.get('urun_kodu', '').strip()
        renk = request.args.get('renk', '').strip()
        konum = request.args.get('konum', '').strip()
        
        if not urun_kodu or not konum:
            return jsonify({
                'success': False,
                'message': 'Ürün kodu ve konum gereklidir'
            })
        
        db = get_db_connection()
        
        # Belirtilen konumdaki stok bilgisini getir
        query = '''
            SELECT * FROM stoklar 
            WHERE urun_kodu = ? AND konum = ?
        '''
        params = [urun_kodu, konum]
        
        if renk:
            query += ' AND renk = ?'
            params.append(renk)
        else:
            query += ' AND (renk IS NULL OR renk = \'\')'
            
        query += ' ORDER BY adet DESC LIMIT 1'  # En çok stoku olan konumu al
        stock = db.execute(query, params).fetchone()
        
        if stock:
            stock_dict = dict(stock)
            return jsonify({
                'success': True,
                'stock': stock_dict
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Bu kombinasyon için stok bulunamadı'
            })
        
    except Exception as e:
        logger.error(f"Stock check API error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Hata: {str(e)}'
        })

@main_bp.route('/stock-exit', methods=['GET', 'POST'])
@admin_required
def stock_exit():
    """Stok çıkış sayfası"""
    if request.method == 'GET':
        # Mevcut ürünler, konumlar ve renkleri getir
        db = get_db_connection()
        products = db.execute('''
            SELECT DISTINCT urun_kodu, urun_adi 
            FROM stoklar 
            WHERE adet > 0 
            ORDER BY urun_kodu
        ''').fetchall()
        
        locations = db.execute('''
            SELECT DISTINCT konum 
            FROM stoklar 
            WHERE konum IS NOT NULL AND adet > 0 
            ORDER BY konum
        ''').fetchall()
        
        colors = db.execute('''
            SELECT DISTINCT renk 
            FROM stoklar 
            WHERE renk IS NOT NULL AND adet > 0 
            ORDER BY renk
        ''').fetchall()
        
        # Bugünün tarihini ekle
        from datetime import date
        today = date.today().strftime('%Y-%m-%d')
        
        return render_template('stock_exit.html', 
                             products=products, 
                             locations=locations, 
                             colors=colors,
                             today=today)
    
    try:
        # Form verilerini al
        urun_kodu = request.form.get('urun_kodu', '').strip().upper()
        renk = request.form.get('renk', '').strip()
        konum = request.form.get('konum', '').strip()
        adet = int(request.form.get('adet', 0))
        aciklama = request.form.get('aciklama', '').strip()
        islem_tarihi = request.form.get('islem_tarihi', '').strip()  # Stok çıkış için tarih eklendi
        
        # Validasyon
        if not urun_kodu:
            flash('Ürün kodu zorunludur', 'error')
            return redirect(request.url)
        
        if not konum:
            flash('Konum zorunludur', 'error')
            return redirect(request.url)
        
        if adet <= 0:
            flash('Adet 0\'dan büyük olmalıdır', 'error')
            return redirect(request.url)
        
        # Stok çıkış işlemini yap
        result = stok_cikis(
            urun_kodu=urun_kodu,
            renk=renk,
            konum=konum,
            adet=adet,
            kullanici='Manuel Çıkış',
            aciklama=aciklama or f'Manuel stok çıkışı: {adet} adet',
            islem_tarihi=islem_tarihi  # Tarih parametresi eklendi
        )
        
        if result['success']:
            flash(f"Stok çıkışı başarılı: {urun_kodu} - {adet} adet çıkarıldı", 'success')
            return redirect(url_for('main.stock_list'))
        else:
            flash(f'Stok çıkış hatası: {result["message"]}', 'error')
            return redirect(request.url)
        
    except ValueError:
        flash('Geçersiz sayısal değer girdiniz', 'error')
        return redirect(request.url)
    except Exception as e:
        logger.error(f"Stock exit error: {str(e)}")
        flash(f'Stok çıkış hatası: {str(e)}', 'error')
        return redirect(request.url)

@main_bp.route('/stock-transfer', methods=['GET', 'POST'])
@admin_required
def stock_transfer():
    """Stok transfer sayfası - konumlar arası transfer"""
    if request.method == 'GET':
        # Mevcut ürünler, konumlar ve renkleri getir
        db = get_db_connection()
        products = db.execute('''
            SELECT DISTINCT urun_kodu, urun_adi 
            FROM stoklar 
            WHERE adet > 0 
            ORDER BY urun_kodu
        ''').fetchall()
        
        locations = db.execute('''
            SELECT DISTINCT konum 
            FROM stoklar 
            WHERE konum IS NOT NULL AND adet > 0 
            ORDER BY konum
        ''').fetchall()
        
        colors = db.execute('''
            SELECT DISTINCT renk 
            FROM stoklar 
            WHERE renk IS NOT NULL AND adet > 0 
            ORDER BY renk
        ''').fetchall()
        
        # Bugünün tarihini ekle
        from datetime import date
        today = date.today().strftime('%Y-%m-%d')
        
        return render_template('stock_transfer.html', 
                             products=products, 
                             locations=locations, 
                             colors=colors,
                             today=today)
    
    try:
        # Form verilerini al
        urun_kodu = request.form.get('urun_kodu', '').strip().upper()
        renk = request.form.get('renk', '').strip()
        kaynak_konum = request.form.get('kaynak_konum', '').strip()
        hedef_konum = request.form.get('hedef_konum', '').strip()
        adet = int(request.form.get('adet', 0))
        aciklama = request.form.get('aciklama', '').strip()
        islem_tarihi = request.form.get('islem_tarihi', '').strip()  # Transfer için tarih eklendi
        
        # Validasyon
        if not urun_kodu:
            flash('Ürün kodu zorunludur', 'error')
            return redirect(request.url)
        
        if not kaynak_konum or not hedef_konum:
            flash('Kaynak ve hedef konum zorunludur', 'error')
            return redirect(request.url)
        
        if kaynak_konum == hedef_konum:
            flash('Kaynak ve hedef konum aynı olamaz', 'error')
            return redirect(request.url)
        
        if adet <= 0:
            flash('Transfer adedi 0\'dan büyük olmalıdır', 'error')
            return redirect(request.url)
        
        # Stok transfer işlemini yap
        result = stok_transfer(
            urun_kodu=urun_kodu,
            renk=renk,
            kaynak_konum=kaynak_konum,
            hedef_konum=hedef_konum,
            adet=adet,
            kullanici='Manuel Transfer',
            islem_tarihi=islem_tarihi  # Tarih parametresi eklendi
        )
        
        if result['success']:
            flash(f"Stok transferi başarılı: {urun_kodu} - {adet} adet {kaynak_konum} → {hedef_konum}", 'success')
            return redirect(url_for('main.stock_list'))
        else:
            flash(f'Stok transfer hatası: {result["message"]}', 'error')
            return redirect(request.url)
        
    except ValueError:
        flash('Geçersiz sayısal değer girdiniz', 'error')
        return redirect(request.url)
    except Exception as e:
        logger.error(f"Stock transfer error: {str(e)}")
        flash(f'Stok transfer hatası: {str(e)}', 'error')
        return redirect(request.url)

@main_bp.route('/api/stock-detail')
def api_stock_detail():
    """Stok detay API endpoint"""
    try:
        urun_kodu = request.args.get('urun_kodu', '').strip()
        renk = request.args.get('renk', '').strip()
        konum = request.args.get('konum', '').strip()
        
        if not urun_kodu:
            return jsonify({
                'success': False,
                'message': 'Ürün kodu gereklidir'
            })
        
        db = get_db_connection()
        
        # İlk olarak ürün var mı kontrol et
        product_exists = db.execute('SELECT COUNT(*) as count FROM stoklar WHERE urun_kodu = ?', [urun_kodu]).fetchone()
        if product_exists['count'] == 0:
            return jsonify({
                'success': False,
                'message': f'Ürün kodu {urun_kodu} sistemde bulunamadı'
            })
        
        # Temel ürün bilgilerini al (herhangi bir konumdan)
        base_query = '''
            SELECT * FROM stoklar 
            WHERE urun_kodu = ?
        '''
        base_params = [urun_kodu]
        
        # Renk filtresi varsa ekle
        if renk:
            base_query += ' AND renk = ?'
            base_params.append(renk)
        
        # Konum filtresi varsa ekle
        if konum:
            base_query += ' AND konum = ?'
            base_params.append(konum)
        
        base_query += ' ORDER BY adet DESC LIMIT 1'
        stock = db.execute(base_query, base_params).fetchone()
        
        if not stock:
            return jsonify({
                'success': False,
                'message': 'Belirtilen kriterlere uygun stok kaydı bulunamadı'
            })
        
        # Aynı ürünün tüm konumlardaki stok durumunu getir
        all_locations_query = '''
            SELECT konum, adet, toplam_kg, rezervasyon_notu
            FROM stoklar 
            WHERE urun_kodu = ?
        '''
        all_params = [urun_kodu]
        
        if renk:
            all_locations_query += ' AND renk = ?'
            all_params.append(renk)
        
        all_locations_query += ' ORDER BY konum'
        
        all_locations = db.execute(all_locations_query, all_params).fetchall()
        
        # Row objelerini dict'e çevir
        stock_dict = dict(stock)
        all_locations_list = [dict(row) for row in all_locations]
        
        return jsonify({
            'success': True,
            'stock': stock_dict,
            'all_locations': all_locations_list
        })
        
    except Exception as e:
        logger.error(f"Stock detail API error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Hata: {str(e)}'
        })

@main_bp.route('/locations')
def locations():
    return render_template('placeholder.html', title='Konumlar', message='Bu özellik sonraki görevlerde eklenecektir.')

@main_bp.route('/stock-report')
@login_required
def stock_report():
    """Detaylı stok raporu - ürün bazında tüm konum dağılımları"""
    # Kullanıcı rol bilgisini al
    current_user = get_current_user()
    user_is_admin = is_admin()
    try:
        db = get_db_connection()
        
        # Arama parametreleri
        search = request.args.get('search', '').strip()
        location_filter = request.args.get('location', '').strip()
        color_filter = request.args.get('color', '').strip()
        
        # Sıralama parametreleri
        sort_by = request.args.get('sort_by', 'urun_kodu')
        sort_order = request.args.get('sort_order', 'asc')
        
        # Geçerli sıralama kolonları
        valid_sort_columns = {
            'urun_kodu': 'urun_kodu',
            'urun_adi': 'urun_adi',
            'renk': 'renk',
            'toplam_adet': 'toplam_adet',
            'toplam_agirlik': 'toplam_agirlik'
        }
        
        # Sıralama parametrelerini doğrula
        if sort_by not in valid_sort_columns:
            sort_by = 'urun_kodu'
        if sort_order not in ['asc', 'desc']:
            sort_order = 'asc'
        
        # Ürün bazında stok özetini getir
        stock_summary_query = '''
            SELECT 
                s.urun_kodu,
                s.urun_adi,
                s.renk,
                s.konum,
                s.adet,
                s.toplam_kg,
                s.kritik_stok_siniri,
                SUM(s.adet) OVER (PARTITION BY s.urun_kodu, s.renk) as toplam_adet,
                SUM(s.toplam_kg) OVER (PARTITION BY s.urun_kodu, s.renk) as toplam_agirlik,
                MIN(s.kritik_stok_siniri) OVER (PARTITION BY s.urun_kodu, s.renk) as min_kritik_sinir
            FROM stoklar s
            WHERE s.adet > 0
            ORDER BY s.urun_kodu, s.renk, s.konum
        '''
        
        stock_summary = db.execute(stock_summary_query).fetchall()
        
        # Verileri ürün bazında grupla
        grouped_products = {}
        for row in stock_summary:
            key = f"{row['urun_kodu']}|{row['renk'] or ''}"
            if key not in grouped_products:
                grouped_products[key] = {
                    'urun_kodu': row['urun_kodu'],
                    'urun_adi': row['urun_adi'],
                    'renk': row['renk'],
                    'toplam_adet': row['toplam_adet'],
                    'toplam_agirlik': row['toplam_agirlik'],
                    'kritik_stok_siniri': row['min_kritik_sinir'] or 5,
                    'is_critical': row['toplam_adet'] <= (row['min_kritik_sinir'] or 5),
                    'konumlar': []
                }
            
            grouped_products[key]['konumlar'].append({
                'konum': row['konum'],
                'adet': row['adet'],
                'toplam_kg': row['toplam_kg'],
                'kritik_stok_siniri': row['kritik_stok_siniri'] or 5,
                'is_critical': row['adet'] <= (row['kritik_stok_siniri'] or 5)
            })
        
        # Yeni tablodan (urun_rezervasyon_notlari) rezervasyon notlarını al
        for key, product in grouped_products.items():
            # Yeni tablodan rezervasyon notunu al
            rezervasyon_notu = get_urun_rezervasyon_notu(product['urun_kodu'], product['renk'] if product['renk'] else None)
            
            # Rezervasyon bilgilerini güncelle
            product['has_reservations'] = rezervasyon_notu is not None and rezervasyon_notu.strip() != ''
            product['reservation_count'] = 1 if product['has_reservations'] else 0
            product['rezervasyon_notu'] = rezervasyon_notu
            
            # Rezervasyon notu varsa, rezervasyon bilgilerini ekle
            if product['has_reservations']:
                # Sayfada gösterilmek üzere rezervasyon bilgileri ekle
                product['reservations'] = [{
                    'konum': 'Tüm Konumlar',
                    'rezervasyon_notu': rezervasyon_notu
                }]
        
        # Filtreleme uygula
        if search:
            filtered_products = {}
            search_lower = search.lower()
            for key, product in grouped_products.items():
                if (search_lower in product['urun_kodu'].lower() or 
                    search_lower in product['urun_adi'].lower()):
                    filtered_products[key] = product
            grouped_products = filtered_products
        
        if location_filter:
            filtered_products = {}
            for key, product in grouped_products.items():
                filtered_locations = [lok for lok in product['konumlar'] if lok['konum'] == location_filter]
                if filtered_locations:
                    new_product = product.copy()
                    new_product['konumlar'] = filtered_locations
                    # Toplamı yeniden hesapla
                    new_product['toplam_adet'] = sum(lok['adet'] for lok in filtered_locations)
                    new_product['toplam_agirlik'] = sum(lok['toplam_kg'] for lok in filtered_locations)
                    filtered_products[key] = new_product
            grouped_products = filtered_products
        
        if color_filter:
            filtered_products = {}
            for key, product in grouped_products.items():
                if product['renk'] == color_filter:
                    filtered_products[key] = product
            grouped_products = filtered_products
        
        # Sıralama uygula
        sort_key_map = {
            'urun_kodu': lambda x: x['urun_kodu'],
            'urun_adi': lambda x: x['urun_adi'],
            'renk': lambda x: x['renk'] or '',
            'toplam_adet': lambda x: x['toplam_adet'],
            'toplam_agirlik': lambda x: x['toplam_agirlik']
        }
        
        sorted_products = sorted(
            grouped_products.values(), 
            key=sort_key_map[sort_by],
            reverse=(sort_order == 'desc')
        )
        
        # Filtre seçenekleri
        locations = db.execute('SELECT DISTINCT konum FROM stoklar WHERE konum IS NOT NULL AND adet > 0 ORDER BY konum').fetchall()
        colors = db.execute('SELECT DISTINCT renk FROM stoklar WHERE renk IS NOT NULL AND adet > 0 ORDER BY renk').fetchall()
        
        # Genel istatistikler
        stats = {
            'total_products': len(sorted_products),
            'total_quantity': sum(p['toplam_adet'] for p in sorted_products),
            'total_weight': sum(p['toplam_agirlik'] for p in sorted_products),
            'total_locations': len(set(lok['konum'] for p in sorted_products for lok in p['konumlar']))
        }
        
        return render_template('stock_report.html',
                             products=sorted_products,
                             locations=locations,
                             colors=colors,
                             stats=stats,
                             search=search,
                             location_filter=location_filter,
                             color_filter=color_filter,
                             sort_by=sort_by,
                             sort_order=sort_order,
                             current_user=current_user,
                             user_is_admin=user_is_admin)
    
    except Exception as e:
        logger.error(f"Stock report error: {str(e)}")
        flash(f'Stok raporu hatası: {str(e)}', 'error')
        return render_template('stock_report.html', products=[], stats={}, locations=[], colors=[],
                             search='', location_filter='', color_filter='', sort_by='urun_kodu', sort_order='asc')

@main_bp.route('/value-report')
def value_report():
    return render_template('placeholder.html', title='Değer Raporu', message='Bu özellik sonraki görevlerde eklenecektir.')

@main_bp.route('/export-excel')
def export_excel():
    return render_template('placeholder.html', title='Excel Export', message='Bu özellik sonraki görevlerde eklenecektir.')

@main_bp.route('/settings')
@admin_required
def settings():
    """Ayarlar ana sayfası"""
    return render_template('settings.html')

@main_bp.route('/settings/critical-stock')
def settings_critical_stock():
    """Kritik stok ayarları sayfası"""
    try:
        db = get_db_connection()
        page = request.args.get('page', 1, type=int)
        per_page = 50
        offset = (page - 1) * per_page
        
        # Arama ve filtreleme
        search = request.args.get('search', '').strip()
        location = request.args.get('location', '').strip()
        color = request.args.get('color', '').strip()
        
        # Base query - ürün bazında grupla
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append('(urun_kodu LIKE ? OR urun_adi LIKE ?)')
            params.extend([f'%{search}%', f'%{search}%'])
        
        if location:
            where_conditions.append('konum = ?')
            params.append(location)
            
        if color:
            where_conditions.append('renk = ?')
            params.append(color)
        
        where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
        
        # Ürün bazında kritik stok ayarları
        query = f'''
            SELECT 
                urun_kodu,
                urun_adi,
                renk,
                SUM(adet) as toplam_adet,
                SUM(toplam_kg) as toplam_agirlik,
                MIN(kritik_stok_siniri) as kritik_stok_siniri,
                SUM(adet) <= MIN(kritik_stok_siniri) as is_critical
            FROM stoklar
            WHERE {where_clause}
            GROUP BY urun_kodu, renk
            ORDER BY is_critical DESC, urun_kodu, renk
            LIMIT ? OFFSET ?
        '''
        critical_stocks = db.execute(query, params + [per_page, offset]).fetchall()
        
        # Toplam kayıt sayısı
        count_query = f'SELECT COUNT(*) as total FROM stoklar WHERE {where_clause} GROUP BY urun_kodu, renk'
        total = db.execute(count_query, params).fetchone()['total']
        
        # Filtre seçenekleri
        locations = db.execute('SELECT DISTINCT konum FROM stoklar WHERE konum IS NOT NULL ORDER BY konum').fetchall()
        colors = db.execute('SELECT DISTINCT renk FROM stoklar WHERE renk IS NOT NULL ORDER BY renk').fetchall()
        
        # Sayfalama bilgileri
        has_prev = page > 1
        has_next = offset + per_page < total
        prev_num = page - 1 if has_prev else None
        next_num = page + 1 if has_next else None
        
        return render_template('settings_critical_stock.html',
                             critical_stocks=critical_stocks,
                             total=total,
                             page=page,
                             per_page=per_page,
                             has_prev=has_prev,
                             has_next=has_next,
                             prev_num=prev_num,
                             next_num=next_num,
                             locations=locations,
                             colors=colors,
                             search=search,
                             location=location,
                             color=color,
                             sort_by=sort_by,
                             sort_order=sort_order)
            SELECT urun_kodu, urun_adi, renk, konum, adet, kritik_stok_siniri,
                   (CASE WHEN adet <= kritik_stok_siniri THEN 1 ELSE 0 END) as is_critical
            FROM stoklar 
            WHERE {where_clause}
            ORDER BY urun_kodu, renk, konum
            LIMIT ? OFFSET ?
        '''
        
        # Toplam kayıt sayısı
        count_query = f'SELECT COUNT(*) as total FROM stoklar WHERE {where_clause}'
        total = db.execute(count_query, params).fetchone()['total']
        
        products = db.execute(query, params + [per_page, offset]).fetchall()
        
        # Filtre seçenekleri
        locations = db.execute('SELECT DISTINCT konum FROM stoklar WHERE konum IS NOT NULL ORDER BY konum').fetchall()
        colors = db.execute('SELECT DISTINCT renk FROM stoklar WHERE renk IS NOT NULL ORDER BY renk').fetchall()
        
        # Sayfalama bilgileri
        has_prev = page > 1
        has_next = offset + per_page < total
        prev_num = page - 1 if has_prev else None
        next_num = page + 1 if has_next else None
        
        return render_template('settings/critical_stock.html',
                             products=products,
                             total=total,
                             page=page,
                             per_page=per_page,
                             has_prev=has_prev,
                             has_next=has_next,
                             prev_num=prev_num,
                             next_num=next_num,
                             locations=locations,
                             colors=colors,
                             search=search,
                             location=location,
                             color=color)
    
    except Exception as e:
        logger.error(f"Critical stock settings error: {str(e)}")
        flash(f'Kritik stok ayarları yüklenirken hata oluştu: {str(e)}', 'error')
        return render_template('settings/critical_stock.html', products=[], total=0)

@main_bp.route('/stock-movements')
def stock_movements():
    """Stok hareketleri sayfası - ürün bazında filtreleme ile"""
    try:
        db = get_db_connection()
        page = request.args.get('page', 1, type=int)
        per_page = 50
        offset = (page - 1) * per_page
        
        # Filtreleme parametreleri
        urun_kodu = request.args.get('urun_kodu', '').strip().upper()
        hareket_tipi = request.args.get('hareket_tipi', '').strip()
        search = request.args.get('search', '').strip()
        
        # Temel sorgu
        where_conditions = []
        params = []
        
        # Ürün kodu filtresi
        if urun_kodu:
            where_conditions.append('h.urun_kodu = ?')
            params.append(urun_kodu)
        
        # Hareket tipi filtresi
        if hareket_tipi and hareket_tipi in ['GIRIS', 'CIKIS', 'TRANSFER']:
            where_conditions.append('h.hareket_tipi = ?')
            params.append(hareket_tipi)
        
        # Genel arama
        if search:
            where_conditions.append('(h.urun_kodu LIKE ? OR h.aciklama LIKE ? OR EXISTS (SELECT 1 FROM stoklar s WHERE s.urun_kodu = h.urun_kodu AND s.urun_adi LIKE ?))')
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param])
        
        where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
        
        # Toplam sayı - güvenli kontrol
        count_query = f'''
            SELECT COUNT(DISTINCT h.id) as total 
            FROM stok_hareketleri h
            WHERE {where_clause}
        '''
        try:
            count_result = db.execute(count_query, params).fetchone()
            total = count_result['total'] if count_result and count_result['total'] is not None else 0
        except Exception as count_error:
            logger.error(f"Count query error: {str(count_error)}")
            total = 0
        
        # Hareketler listesi - güvenli kontrol
        movements = []
        try:
            movements_query = f'''
                SELECT DISTINCT h.id, h.urun_kodu, h.hareket_tipi, h.miktar, 
                       h.onceki_miktar, h.yeni_miktar, h.konum, h.aciklama, 
                       h.kullanici, h.tarih,
                       (SELECT s2.urun_adi FROM stoklar s2 WHERE s2.urun_kodu = h.urun_kodu LIMIT 1) as urun_adi,
                       DATE(h.tarih) as tarih_str,
                       TIME(h.tarih) as saat_str
                FROM stok_hareketleri h
                WHERE {where_clause}
                ORDER BY h.tarih DESC
                LIMIT ? OFFSET ?
            '''
            movements = db.execute(movements_query, params + [per_page, offset]).fetchall()
        except Exception as movements_error:
            logger.error(f"Movements query error: {str(movements_error)}")
            movements = []
        
        # Filtreleme için seçenekler - güvenli kontrol
        products = []
        try:
            products = db.execute('''
                SELECT DISTINCT h.urun_kodu, 
                       (SELECT s2.urun_adi FROM stoklar s2 WHERE s2.urun_kodu = h.urun_kodu LIMIT 1) as urun_adi
                FROM stok_hareketleri h
                ORDER BY h.urun_kodu
            ''').fetchall()
        except Exception as products_error:
            logger.error(f"Products query error: {str(products_error)}")
            products = []
        
        # Sayfalama bilgileri
        has_prev = page > 1
        has_next = offset + per_page < total
        prev_num = page - 1 if has_prev else None
        next_num = page + 1 if has_next else None
        
        return render_template('stock_movements.html',
                             movements=movements,
                             total=total,
                             page=page,
                             per_page=per_page,
                             has_prev=has_prev,
                             has_next=has_next,
                             prev_num=prev_num,
                             next_num=next_num,
                             products=products,
                             urun_kodu=urun_kodu,
                             hareket_tipi=hareket_tipi,
                             search=search)
                             
    except Exception as e:
        logger.error(f"Stock movements error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash(f'Stok hareketleri yüklenirken hata oluştu: {str(e)}', 'error')
        return render_template('stock_movements.html', movements=[], total=0, products=[])

@main_bp.route('/api/product-movements')
def api_product_movements():
    """Belirli bir ürün için stok hareketlerini getir"""
    try:
        urun_kodu = request.args.get('urun_kodu', '').strip().upper()
        limit = request.args.get('limit', 20, type=int)
        
        if not urun_kodu:
            return jsonify({'success': False, 'message': 'Ürün kodu gereklidir'})
        
        db = get_db_connection()
        
        # Ürün hareketlerini getir
        movements = db.execute('''
            SELECT DISTINCT h.id, h.urun_kodu, h.hareket_tipi, h.miktar,
                   h.onceki_miktar, h.yeni_miktar, h.konum, h.aciklama,
                   h.kullanici, h.tarih,
                   (SELECT s2.urun_adi FROM stoklar s2 WHERE s2.urun_kodu = h.urun_kodu LIMIT 1) as urun_adi,
                   DATE(h.tarih) as tarih_str,
                   TIME(h.tarih) as saat_str
            FROM stok_hareketleri h
            WHERE h.urun_kodu = ?
            ORDER BY h.tarih DESC
            LIMIT ?
        ''', (urun_kodu, limit)).fetchall()
        
        if not movements:
            return jsonify({
                'success': False, 
                'message': f'{urun_kodu} kodlu ürün için hareket bulunamadı'
            })
        
        # JSON formatına çevir
        movements_list = []
        for mov in movements:
            movements_list.append({
                'id': mov['id'],
                'hareket_tipi': mov['hareket_tipi'],
                'miktar': mov['miktar'],
                'onceki_miktar': mov['onceki_miktar'],
                'yeni_miktar': mov['yeni_miktar'],
                'konum': mov['konum'],
                'aciklama': mov['aciklama'],
                'kullanici': mov['kullanici'],
                'tarih_str': mov['tarih_str'],
                'saat_str': mov['saat_str']
            })
        
        return jsonify({
            'success': True,
            'urun_kodu': urun_kodu,
            'urun_adi': movements[0]['urun_adi'] if movements[0]['urun_adi'] else 'Bilinmeyen Ürün',
            'movements': movements_list,
            'total': len(movements_list)
        })
        
    except Exception as e:
        logger.error(f"Product movements API error: {str(e)}")
        return jsonify({'success': False, 'message': 'Sunucu hatası'}), 500

@main_bp.route('/search')
def search():
    return redirect(url_for('main.stock_list', search=request.args.get('q', '')))

@main_bp.route('/api/search-products')
def api_search_products():
    """Ürün arama API - autocomplete için"""
    try:
        query = request.args.get('q', '').strip()
        if len(query) < 2:  # En az 2 karakter
            return jsonify([])
        
        db = get_db_connection()
        
        # Ürün kodu ve ürün adında arama yap
        results = db.execute('''
            SELECT DISTINCT urun_kodu, urun_adi, renk, konum, adet, toplam_kg
            FROM stoklar 
            WHERE (urun_kodu LIKE ? OR urun_adi LIKE ?)
            AND adet > 0
            ORDER BY 
                CASE 
                    WHEN urun_kodu LIKE ? THEN 1 
                    WHEN urun_adi LIKE ? THEN 2 
                    ELSE 3 
                END,
                urun_kodu
            LIMIT 10
        ''', (f'%{query}%', f'%{query}%', f'{query}%', f'{query}%')).fetchall()
        
        # JSON formatına çevir
        products = []
        for row in results:
            products.append({
                'urun_kodu': row['urun_kodu'],
                'urun_adi': row['urun_adi'],
                'renk': row['renk'] or '',
                'konum': row['konum'] or '',
                'adet': row['adet'],
                'toplam_kg': float(row['toplam_kg']) if row['toplam_kg'] else 0,
                'display_text': f"{row['urun_kodu']} - {row['urun_adi']}" + (f" ({row['renk']})" if row['renk'] else ""),
                'detail_text': f"Stok: {row['adet']} adet" + (f" - {row['konum']}" if row['konum'] else "")
            })
        
        return jsonify(products)
    
    except Exception as e:
        logger.error(f"Product search API error: {str(e)}")
        return jsonify([]), 500

@main_bp.route('/api/product-detail')
def api_product_detail():
    """Ürün detay API - ürün bazında tüm konum bilgileri"""
    try:
        urun_kodu = request.args.get('urun_kodu', '').strip().upper()
        renk = request.args.get('renk', '').strip()
        
        if not urun_kodu:
            return jsonify({'success': False, 'message': 'Ürün kodu gereklidir'})
        
        # Ürün bazında tüm konum bilgilerini getir
        locations = get_all_locations_for_product(urun_kodu, renk or None)
        
        if not locations:
            return jsonify({'success': False, 'message': 'Ürün bulunamadı'})
        
        # Ürün bilgisini al
        db = get_db_connection()
        if renk:
            product_info = db.execute('''
                SELECT DISTINCT urun_kodu, urun_adi, renk
                FROM stoklar 
                WHERE urun_kodu = ? AND renk = ?
            ''', (urun_kodu, renk)).fetchone()
        else:
            product_info = db.execute('''
                SELECT DISTINCT urun_kodu, urun_adi, renk
                FROM stoklar 
                WHERE urun_kodu = ?
                LIMIT 1
            ''', (urun_kodu,)).fetchone()
        
        if not product_info:
            return jsonify({'success': False, 'message': 'Ürün bilgisi bulunamadı'})
        
        # Konum verilerini düzenle
        konumlar = []
        toplam_adet = 0
        toplam_agirlik = 0
        rezervasyon_bilgileri = []
        
        for loc in locations:
            konum_data = {
                'konum': loc['konum'],
                'adet': loc['adet'] if 'adet' in loc.keys() else loc[1],
                'toplam_kg': float(loc['toplam_kg']) if 'toplam_kg' in loc.keys() else float(loc[2] if loc[2] else 0)
            }
            
            # Rezervasyon notunu kontrol et - artık ürün bazlı
            rezervasyon_notu = get_urun_rezervasyon_notu(urun_kodu, renk if renk else None)
            if rezervasyon_notu:
                konum_data['rezervasyon_notu'] = rezervasyon_notu
                # Tüm konumlar için aynı rezervasyon notunu göster
                if not any(rb['not'] == rezervasyon_notu for rb in rezervasyon_bilgileri):
                    rezervasyon_bilgileri.append({
                        'konum': 'Tüm Konumlar',
                        'not': rezervasyon_notu
                    })
            
            konumlar.append(konum_data)
            toplam_adet += konum_data['adet']
            toplam_agirlik += konum_data['toplam_kg']
        
        return jsonify({
            'success': True,
            'product': {
                'urun_kodu': product_info['urun_kodu'],
                'urun_adi': product_info['urun_adi'],
                'renk': product_info['renk'] or '',
                'toplam_adet': toplam_adet,
                'toplam_agirlik': round(toplam_agirlik, 2),
                'konumlar': konumlar,
                'rezervasyon_bilgileri': rezervasyon_bilgileri
            }
        })
    
    except Exception as e:
        logger.error(f"Product detail API error: {str(e)}")
        return jsonify({'success': False, 'message': 'Sunucu hatası'}), 500

# ==== REZERVASYON ENDPOINT'LERİ ====

# Reservation system routes - Disabled (using inline notes only)
# @main_bp.route('/rezervasyonlar')
# def rezervasyonlar():
#     """Rezervasyon listesi sayfası"""
    try:
        db = get_db_connection()
        page = request.args.get('page', 1, type=int)
        per_page = 50
        offset = (page - 1) * per_page
        
        # Arama ve filtreleme
        search = request.args.get('search', '').strip()
        konum = request.args.get('konum', '').strip()
        durum = request.args.get('durum', '').strip()
        rezerve_eden = request.args.get('rezerve_eden', '').strip()
        
        # Base query
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append('(r.urun_kodu LIKE ? OR r.urun_adi LIKE ? OR r.rezerve_eden LIKE ?)')
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
        
        if konum:
            where_conditions.append('r.konum = ?')
            params.append(konum)
            
        if durum:
            where_conditions.append('r.durum = ?')
            params.append(durum)
            
        if rezerve_eden:
            where_conditions.append('r.rezerve_eden = ?')
            params.append(rezerve_eden)
        
        where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
        
        # Toplam kayıt sayısı
        count_query = f'SELECT COUNT(*) as total FROM rezervasyonlar r WHERE {where_clause}'
        total = db.execute(count_query, params).fetchone()['total']
        
        # Rezervasyon listesi
        query = f'''
            SELECT r.* FROM rezervasyonlar r
            WHERE {where_clause}
            ORDER BY r.rezerve_tarihi DESC
            LIMIT ? OFFSET ?
        '''
        rezervasyonlar_list = db.execute(query, params + [per_page, offset]).fetchall()
        
        # Filtre seçenekleri
        locations = db.execute('SELECT DISTINCT konum FROM rezervasyonlar ORDER BY konum').fetchall()
        users = db.execute('SELECT DISTINCT rezerve_eden FROM rezervasyonlar ORDER BY rezerve_eden').fetchall()
        
        # Sayfalama bilgileri
        has_prev = page > 1
        has_next = offset + per_page < total
        prev_num = page - 1 if has_prev else None
        next_num = page + 1 if has_next else None
        
        return render_template('rezervasyonlar.html',
                             rezervasyonlar=rezervasyonlar_list,
                             total=total,
                             page=page,
                             per_page=per_page,
                             has_prev=has_prev,
                             has_next=has_next,
                             prev_num=prev_num,
                             next_num=next_num,
                             locations=locations,
                             users=users,
                             search=search,
                             konum=konum,
                             durum=durum,
                             rezerve_eden=rezerve_eden)
    
    except Exception as e:
        logger.error(f"Rezervasyon list error: {str(e)}")
        flash(f'Rezervasyon listesi yüklenirken hata oluştu: {str(e)}', 'error')
        return render_template('rezervasyonlar.html', rezervasyonlar=[], total=0)

# @main_bp.route('/rezervasyon-olustur', methods=['GET', 'POST'])
# def rezervasyon_olustur_sayfa():
#     """Rezervasyon oluşturma sayfası"""
    if request.method == 'GET':
        # Mevcut ürünler, konumlar ve renkleri getir
        db = get_db_connection()
        products = db.execute('''
            SELECT DISTINCT urun_kodu, urun_adi 
            FROM stoklar 
            WHERE adet > 0
            ORDER BY urun_kodu
        ''').fetchall()
        
        locations = db.execute('''
            SELECT DISTINCT konum 
            FROM stoklar 
            WHERE konum IS NOT NULL AND adet > 0
            ORDER BY konum
        ''').fetchall()
        
        colors = db.execute('''
            SELECT DISTINCT renk 
            FROM stoklar 
            WHERE renk IS NOT NULL AND adet > 0
            ORDER BY renk
        ''').fetchall()
        
        return render_template('rezervasyon_olustur.html', 
                             products=products, 
                             locations=locations, 
                             colors=colors)
    
    try:
        # Form verilerini al
        urun_kodu = request.form.get('urun_kodu', '').strip().upper()
        urun_adi = request.form.get('urun_adi', '').strip()
        renk = request.form.get('renk', '').strip()
        konum = request.form.get('konum', '').strip()
        adet = int(request.form.get('adet', 0))
        rezerve_eden = request.form.get('rezerve_eden', '').strip()
        aciklama = request.form.get('aciklama', '').strip()
        
        # Validasyon
        if not urun_kodu:
            flash('Ürün kodu zorunludur', 'error')
            return redirect(request.url)
        
        if not konum:
            flash('Konum zorunludur', 'error')
            return redirect(request.url)
        
        if adet <= 0:
            flash('Rezerve edilecek adet 0\'dan büyük olmalıdır', 'error')
            return redirect(request.url)
            
        if not rezerve_eden:
            flash('Rezerve eden kişi bilgisi zorunludur', 'error')
            return redirect(request.url)
        
        # Rezervasyon oluştur
        result = rezervasyon_olustur(
            urun_kodu=urun_kodu,
            urun_adi=urun_adi,
            renk=renk,
            konum=konum,
            adet=adet,
            rezerve_eden=rezerve_eden,
            aciklama=aciklama
        )
        
        if result['success']:
            flash(f"Rezervasyon başarıyla oluşturuldu: {urun_kodu} - {adet} adet", 'success')
            return redirect(url_for('main.rezervasyonlar'))
        else:
            flash(f'Rezervasyon oluşturma hatası: {result["message"]}', 'error')
            return redirect(request.url)
        
    except ValueError as e:
        flash('Geçersiz sayısal değer girdiniz', 'error')
        return redirect(request.url)
    except Exception as e:
        logger.error(f"Rezervasyon create error: {str(e)}")
        flash(f'Rezervasyon oluşturma hatası: {str(e)}', 'error')
        return redirect(request.url)

# @main_bp.route('/api/rezervasyon-stok-kontrol')
# def api_rezervasyon_stok_kontrol():
#     """Rezervasyon için stok kontrol API"""
    try:
        urun_kodu = request.args.get('urun_kodu', '').strip()
        renk = request.args.get('renk', '').strip()
        konum = request.args.get('konum', '').strip()
        
        if not urun_kodu or not konum:
            return jsonify({
                'success': False,
                'message': 'Ürün kodu ve konum gereklidir'
            })
        
        # Ürün rezervasyon durumunu getir
        durum = get_urun_rezervasyon_durumu(urun_kodu, renk, konum)
        
        if durum:
            stok_bilgisi = durum[0]  # İlk kayıt
            return jsonify({
                'success': True,
                'mevcut_stok': stok_bilgisi['mevcut_stok'],
                'rezerveli_adet': stok_bilgisi['rezerveli_adet'],
                'musait_adet': stok_bilgisi['musait_adet']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Bu konumda stok bulunamadı'
            })
        
    except Exception as e:
        logger.error(f"Rezervasyon stok kontrol API error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Hata: {str(e)}'
        })

# @main_bp.route('/api/rezervasyon-tamamla', methods=['POST'])
# def api_rezervasyon_tamamla():
#     """Rezervasyon tamamlama API"""
    try:
        data = request.get_json()
        rezervasyon_id = data.get('rezervasyon_id')
        aciklama = data.get('aciklama', '')
        
        if not rezervasyon_id:
            return jsonify({'success': False, 'message': 'Rezervasyon ID gereklidir'})
        
        result = rezervasyon_tamamla(
            rezervasyon_id=rezervasyon_id,
            kullanici='Web Kullanıcısı',
            aciklama=aciklama
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Rezervasyon tamamlama API error: {str(e)}")
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'})

# @main_bp.route('/api/rezervasyon-iptal', methods=['POST'])
# def api_rezervasyon_iptal():
#     """Rezervasyon iptal API"""
    try:
        data = request.get_json()
        rezervasyon_id = data.get('rezervasyon_id')
        aciklama = data.get('aciklama', '')
        
        if not rezervasyon_id:
            return jsonify({'success': False, 'message': 'Rezervasyon ID gereklidir'})
        
        result = rezervasyon_iptal(
            rezervasyon_id=rezervasyon_id,
            kullanici='Web Kullanıcısı',
            aciklama=aciklama
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Rezervasyon iptal API error: {str(e)}")
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'})

# @main_bp.route('/api/rezervasyon-detay/<int:rezervasyon_id>')
# def api_rezervasyon_detay(rezervasyon_id):
#     """Rezervasyon detay API"""
    try:
        db = get_db_connection()
        
        # Rezervasyon bilgisini getir
        rezervasyon = db.execute(
            'SELECT * FROM rezervasyonlar WHERE id = ?',
            (rezervasyon_id,)
        ).fetchone()
        
        if not rezervasyon:
            return jsonify({'success': False, 'message': 'Rezervasyon bulunamadı'})
        
        # Rezervasyon hareketlerini getir
        hareketler = db.execute('''
            SELECT * FROM rezervasyon_hareketleri 
            WHERE rezervasyon_id = ? 
            ORDER BY tarih DESC
        ''', (rezervasyon_id,)).fetchall()
        
        # Dict'e çevir
        rezervasyon_dict = dict(rezervasyon)
        hareketler_list = [dict(row) for row in hareketler]
        
        return jsonify({
            'success': True,
            'rezervasyon': rezervasyon_dict,
            'hareketler': hareketler_list
        })
        
    except Exception as e:
        logger.error(f"Rezervasyon detay API error: {str(e)}")
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'})

@main_bp.route('/api/rezervasyon-notu-kaydet', methods=['POST'])
def api_rezervasyon_notu_kaydet():
    """Rezervasyon notu kaydetme API - artık ürün bazlı"""
    try:
        data = request.get_json()
        urun_kodu = data.get('urun_kodu', '').strip()
        renk = data.get('renk', '').strip() if data.get('renk') else None
        note = data.get('note', '').strip()
        
        if not urun_kodu:
            return jsonify({'success': False, 'message': 'Ürün kodu gereklidir'})
        
        # Veritabanında güncelle - tüm konumlar için aynı notu kaydet
        db = get_db_connection()
        
        # Önce kayıt var mı kontrol et
        if renk:
            existing = db.execute(
                'SELECT id FROM stoklar WHERE urun_kodu = ? AND renk = ? LIMIT 1',
                (urun_kodu, renk)
            ).fetchone()
        else:
            existing = db.execute(
                'SELECT id FROM stoklar WHERE urun_kodu = ? AND (renk IS NULL OR renk = "") LIMIT 1',
                (urun_kodu,)
            ).fetchone()
        
        if not existing:
            return jsonify({'success': False, 'message': 'Ürün kaydı bulunamadı'})
        
        # Tüm konumlar için aynı rezervasyon notunu güncelle
        if renk:
            db.execute(
                'UPDATE stoklar SET rezervasyon_notu = ? WHERE urun_kodu = ? AND renk = ?',
                (note, urun_kodu, renk)
            )
        else:
            db.execute(
                'UPDATE stoklar SET rezervasyon_notu = ? WHERE urun_kodu = ? AND (renk IS NULL OR renk = "")',
                (note, urun_kodu)
            )
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rezervasyon notu başarıyla kaydedildi'
        })
        
    except Exception as e:
        logger.error(f"Rezervasyon notu kaydetme API error: {str(e)}")
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'})

@main_bp.route('/api/save-critical-threshold', methods=['POST'])
def api_save_critical_threshold():
    """Kritik stok sınırı kaydetme API"""
    try:
        data = request.get_json()
        urun_kodu = data.get('urun_kodu', '').strip()
        renk = data.get('renk', '').strip() if data.get('renk') else None
        konum = data.get('konum', '').strip()
        kritik_sinir = data.get('kritik_sinir', 5)
        
        if not urun_kodu or not konum:
            return jsonify({'success': False, 'message': 'Ürün kodu ve konum gereklidir'})
        
        # Kritik sınır validasyonu
        try:
            kritik_sinir = int(kritik_sinir)
            if kritik_sinir < 0:
                return jsonify({'success': False, 'message': 'Kritik sınır 0\'dan küçük olamaz'})
        except (ValueError, TypeError):
            kritik_sinir = 5  # Varsayılan değer
        
        # Veritabanında güncelle
        db = get_db_connection()
        
        # Önce kayıt var mı kontrol et
        if renk:
            existing = db.execute(
                'SELECT id FROM stoklar WHERE urun_kodu = ? AND renk = ? AND konum = ?',
                (urun_kodu, renk, konum)
            ).fetchone()
        else:
            existing = db.execute(
                'SELECT id FROM stoklar WHERE urun_kodu = ? AND (renk IS NULL OR renk = "") AND konum = ?',
                (urun_kodu, konum)
            ).fetchone()
        
        if not existing:
            return jsonify({'success': False, 'message': 'Stok kaydı bulunamadı'})
        
        # Kritik stok sınırını güncelle
        if renk:
            db.execute(
                'UPDATE stoklar SET kritik_stok_siniri = ? WHERE urun_kodu = ? AND renk = ? AND konum = ?',
                (kritik_sinir, urun_kodu, renk, konum)
            )
        else:
            db.execute(
                'UPDATE stoklar SET kritik_stok_siniri = ? WHERE urun_kodu = ? AND (renk IS NULL OR renk = "") AND konum = ?',
                (kritik_sinir, urun_kodu, konum)
            )
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': f'Kritik stok sınırı {kritik_sinir} olarak kaydedildi'
        })
        
    except Exception as e:
        logger.error(f"Kritik stok sınırı kaydetme API error: {str(e)}")
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'})

@main_bp.route('/export-all-stocks')
def export_all_stocks():
    """Tüm stokları Excel olarak indir"""
    try:
        import pandas as pd
        from io import BytesIO
        from datetime import datetime
        
        db = get_db_connection()
        
        # Tüm stok verilerini getir
        stocks = db.execute('''
            SELECT 
                s.urun_kodu,
                s.urun_adi,
                s.renk,
                s.sistem_seri,
                s.uzunluk,
                s.mt_kg,
                s.boy_kg,
                s.adet,
                s.toplam_kg,
                s.konum,
                s.rezervasyon_notu,
                s.kritik_stok_siniri,
                s.created_at,
                s.updated_at
            FROM stoklar s
            ORDER BY s.urun_kodu, s.renk, s.konum
        ''').fetchall()
        
        # DataFrame'e çevir
        df = pd.DataFrame([dict(row) for row in stocks])
        
        if df.empty:
            # Boş dosya oluştur
            df = pd.DataFrame(columns=[
                'urun_kodu', 'urun_adi', 'renk', 'sistem_seri', 'uzunluk',
                'mt_kg', 'boy_kg', 'adet', 'toplam_kg', 'konum',
                'rezervasyon_notu', 'kritik_stok_siniri', 'created_at', 'updated_at'
            ])
        
        # Excel dosyası oluştur
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Stoklar', index=False)
            
            # Worksheet'i al ve formatla
            worksheet = writer.sheets['Stoklar']
            
            # Kolon genişliklerini ayarla
            column_widths = {
                'A': 15,  # urun_kodu
                'B': 30,  # urun_adi
                'C': 12,  # renk
                'D': 15,  # sistem_seri
                'E': 10,  # uzunluk
                'F': 10,  # mt_kg
                'G': 10,  # boy_kg
                'H': 8,   # adet
                'I': 12,  # toplam_kg
                'J': 15,  # konum
                'K': 25,  # rezervasyon_notu
                'L': 12,  # kritik_stok_siniri
                'M': 20,  # created_at
                'N': 20   # updated_at
            }
            
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width
            
            # Header stilini ayarla
            from openpyxl.styles import Font, PatternFill
            header_font = Font(bold=True, color='FFFFFF')
            header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
            
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
        
        output.seek(0)
        
        # Dosya adı oluştur
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tum_stoklar_{timestamp}.xlsx'
        
        response = make_response(output.read())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        logger.error(f"Excel export error: {str(e)}")
        flash(f'Excel dosyası oluşturulurken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.settings'))

@main_bp.route('/import-and-update-stocks', methods=['POST'])
def import_and_update_stocks():
    """Excel dosyasından stokları import et ve veritabanını güncelle"""
    try:
        import pandas as pd
        from datetime import datetime
        import os
        
        # Dosya kontrolü
        if 'excel_file' not in request.files:
            flash('Dosya seçilmedi!', 'error')
            return redirect(url_for('main.settings'))
        
        file = request.files['excel_file']
        if file.filename == '':
            flash('Dosya seçilmedi!', 'error')
            return redirect(url_for('main.settings'))
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            flash('Sadece Excel dosyaları (.xlsx, .xls) kabul edilir!', 'error')
            return redirect(url_for('main.settings'))
        
        # Excel dosyasını oku
        try:
            df = pd.read_excel(file, sheet_name='Stoklar')
        except Exception as e:
            flash(f'Excel dosyası okunamadı: {str(e)}', 'error')
            return redirect(url_for('main.settings'))
        
        # Gerekli kolonları kontrol et
        required_columns = [
            'urun_kodu', 'urun_adi', 'renk', 'sistem_seri', 'uzunluk',
            'mt_kg', 'boy_kg', 'adet', 'toplam_kg', 'konum',
            'rezervasyon_notu', 'kritik_stok_siniri'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            flash(f'Eksik kolonlar: {missing_columns}', 'error')
            return redirect(url_for('main.settings'))
        
        # Veri doğrulama
        errors = []
        for index, row in df.iterrows():
            if pd.isna(row['urun_kodu']) or str(row['urun_kodu']).strip() == '':
                errors.append(f'Satır {index + 2}: Ürün kodu boş olamaz')
            if pd.isna(row['urun_adi']) or str(row['urun_adi']).strip() == '':
                errors.append(f'Satır {index + 2}: Ürün adı boş olamaz')
            if pd.isna(row['konum']) or str(row['konum']).strip() == '':
                errors.append(f'Satır {index + 2}: Konum boş olamaz')
            if pd.isna(row['adet']) or float(row['adet']) < 0:
                errors.append(f'Satır {index + 2}: Adet 0 veya pozitif olmalı')
        
        if errors:
            flash(f'Veri hataları bulundu: {"; ".join(errors[:5])}', 'error')
            return redirect(url_for('main.settings'))
        
        # Veritabanını güncelle
        db = get_db_connection()
        
        # Mevcut verileri yedekle (opsiyonel)
        backup_table = f'stoklar_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        db.execute(f'CREATE TABLE {backup_table} AS SELECT * FROM stoklar')
        
        # Mevcut stokları temizle
        db.execute('DELETE FROM stoklar')
        
        # Yeni verileri ekle
        insert_count = 0
        for index, row in df.iterrows():
            try:
                db.execute('''
                    INSERT INTO stoklar (
                        urun_kodu, urun_adi, renk, sistem_seri, uzunluk,
                        mt_kg, boy_kg, adet, toplam_kg, konum,
                        rezervasyon_notu, kritik_stok_siniri, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                ''', (
                    str(row['urun_kodu']).strip(),
                    str(row['urun_adi']).strip(),
                    str(row['renk']).strip() if pd.notna(row['renk']) else None,
                    str(row['sistem_seri']).strip() if pd.notna(row['sistem_seri']) else None,
                    float(row['uzunluk']) if pd.notna(row['uzunluk']) else None,
                    float(row['mt_kg']) if pd.notna(row['mt_kg']) else None,
                    float(row['boy_kg']) if pd.notna(row['boy_kg']) else None,
                    int(row['adet']) if pd.notna(row['adet']) else 0,
                    float(row['toplam_kg']) if pd.notna(row['toplam_kg']) else None,
                    str(row['konum']).strip(),
                    str(row['rezervasyon_notu']).strip() if pd.notna(row['rezervasyon_notu']) else None,
                    int(row['kritik_stok_siniri']) if pd.notna(row['kritik_stok_siniri']) else 5
                ))
                insert_count += 1
            except Exception as e:
                logger.error(f"Satır {index + 2} import hatası: {str(e)}")
                continue
        
        db.commit()
        
        flash(f'Başarıyla {insert_count} stok kaydı import edildi! Veritabanı güncellendi.', 'success')
        return redirect(url_for('main.settings'))
        
    except Exception as e:
        logger.error(f"Excel import error: {str(e)}")
        flash(f'Import işlemi sırasında hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.settings'))