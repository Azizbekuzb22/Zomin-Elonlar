import os
import uuid
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
from database import get_db_connection, init_db
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Read secrets from environment variables, fallback to defaults
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-fallback-secret')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ADMIN_USERNAME'] = os.getenv('ADMIN_USERNAME', 'admin')
app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD', 'admin')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database if it doesn't exist
if not os.path.exists(os.path.join(os.path.dirname(__file__), 'zomin_market.db')):
    init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator: admin login talab qiladi."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Iltimos, avval admin sifatida kiring.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

@app.template_filter('timeago')
def timeago_filter(dt_str):
    if not dt_str: return ''
    try:
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return dt_str
    now = datetime.now()
    diff = now - dt
    if diff.days > 365:
        return f'{diff.days // 365} yil oldin'
    if diff.days > 30:
        return f'{diff.days // 30} oy oldin'
    if diff.days > 0:
        return f'{diff.days} kun oldin'
    if diff.seconds > 3600:
        return f'{diff.seconds // 3600} soat oldin'
    if diff.seconds > 60:
        return f'{diff.seconds // 60} daqiqa oldin'
    return 'hozirgina'

@app.context_processor
def inject_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories ORDER BY id').fetchall()
    conn.close()
    return dict(categories=categories)

@app.route('/')
def index():
    conn = get_db_connection()
    q = request.args.get('q', '').strip()
    
    # Faol bannerlarni yuklash
    banners = conn.execute(
        'SELECT * FROM banners WHERE is_active = 1 ORDER BY created_at DESC'
    ).fetchall()
    
    if q:
        pinned_listings = []
        top_listings = []
        regular_listings = conn.execute(
            '''
            SELECT l.*, c.name as category_name, c.slug as category_slug 
            FROM listings l 
            JOIN categories c ON l.category_id = c.id 
            WHERE l.title LIKE ? OR l.description LIKE ?
            ORDER BY l.created_at DESC LIMIT 20
            ''', ('%'+q+'%', '%'+q+'%')
        ).fetchall()
    else:
        # Pinlangan e'lonlar eng birinchi
        pinned_listings = conn.execute(
            '''
            SELECT l.*, c.name as category_name, c.slug as category_slug
            FROM listings l 
            JOIN categories c ON l.category_id = c.id 
            WHERE l.is_pinned = 1 
            ORDER BY l.created_at DESC
            '''
        ).fetchall()
        top_listings = conn.execute(
            '''
            SELECT l.*, c.name as category_name, c.slug as category_slug
            FROM listings l 
            JOIN categories c ON l.category_id = c.id 
            WHERE l.is_top = 1 AND l.is_pinned = 0
            ORDER BY l.created_at DESC LIMIT 8
            '''
        ).fetchall()
        regular_listings = conn.execute(
            '''
            SELECT l.*, c.name as category_name, c.slug as category_slug 
            FROM listings l 
            JOIN categories c ON l.category_id = c.id 
            WHERE l.is_top = 0 AND l.is_pinned = 0
            ORDER BY l.created_at DESC LIMIT 12
            '''
        ).fetchall()
    conn.close()
    
    return render_template('index.html',
        pinned_listings=pinned_listings,
        top_listings=top_listings,
        listings=regular_listings,
        banners=banners,
        query=q)

@app.route('/category/<slug>')
def category_view(slug):
    conn = get_db_connection()
    cat = conn.execute('SELECT * FROM categories WHERE slug = ?', (slug,)).fetchone()
    if cat is None:
        abort(404)
        
    cursor = conn.execute(
        '''
        SELECT l.*, c.name as category_name, c.slug as category_slug 
        FROM listings l 
        JOIN categories c ON l.category_id = c.id 
        WHERE l.category_id = ? 
        ORDER BY l.is_top DESC, l.created_at DESC
        ''', (cat['id'],)
    )
    listings = cursor.fetchall()
    conn.close()
    return render_template('listings.html', listings=listings, current_category=cat)

@app.route('/favorites')
def favorites():
    ids_param = request.args.get('ids', '')
    if not ids_param:
        return render_template('listings.html', listings=[], page_title="Saralangan e'lonlar")
        
    ids_list = [int(id.strip()) for id in ids_param.split(',') if id.strip().isdigit()]
    if not ids_list:
        return render_template('listings.html', listings=[], page_title="Saralangan e'lonlar")

    conn = get_db_connection()
    placeholders = ','.join('?' * len(ids_list))
    cursor = conn.execute(
        f'''
        SELECT l.*, c.name as category_name, c.slug as category_slug 
        FROM listings l 
        JOIN categories c ON l.category_id = c.id 
        WHERE l.id IN ({placeholders})
        ORDER BY l.created_at DESC
        ''', ids_list
    )
    listings = cursor.fetchall()
    conn.close()
    return render_template('listings.html', listings=listings, page_title="Saralangan e'lonlar")

@app.route('/add', methods=['GET', 'POST'])
def add_listing():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        category_id = request.form.get('category_id')
        condition = request.form.get('condition', 'Noma\'lum')
        contact_phone = request.form.get('contact_phone', '').strip()
        contact_telegram = request.form.get('contact_telegram', '').strip()
        
        if contact_telegram.startswith('@'):
            contact_telegram = contact_telegram[1:]
            
        if not title or not price or not category_id:
            flash('Sarlavha, Narx va Kategoriya kiritilishi shart.', 'error')
            return redirect(url_for('add_listing'))

        file = request.files.get('image')
        filename = None
        if file and file.filename != '' and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        try:
            price_val = float(price)
        except ValueError:
            flash('Narx formati noto\'g\'ri.', 'error')
            return redirect(url_for('add_listing'))

        conn = get_db_connection()
        conn.execute(
            '''
            INSERT INTO listings 
            (title, description, price, category_id, condition, contact_phone, contact_telegram, image_filename) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (title, description, price_val, category_id, condition, contact_phone, contact_telegram, filename)
        )
        conn.commit()
        conn.close()
        flash('E\'lon muvaffaqiyatli qo\'shildi!', 'success')
        return redirect(url_for('index'))
        
    return render_template('add_listing.html')

@app.route('/listing/<int:listing_id>')
def single_listing(listing_id):
    conn = get_db_connection()
    
    # Prosmotr (views) sonini 1 taga oshiramiz
    conn.execute('UPDATE listings SET views = views + 1 WHERE id = ?', (listing_id,))
    conn.commit()

    listing = conn.execute(
        '''
        SELECT l.*, c.name as category_name, c.slug as category_slug
        FROM listings l 
        JOIN categories c ON l.category_id = c.id 
        WHERE l.id = ?
        ''', (listing_id,)
    ).fetchone()
    
    if listing is None:
        abort(404)
        
    cursor = conn.execute(
        '''
        SELECT l.*, c.name as category_name, c.slug as category_slug 
        FROM listings l 
        JOIN categories c ON l.category_id = c.id 
        WHERE l.category_id = ? AND l.id != ? 
        ORDER BY l.created_at DESC LIMIT 4
        ''', (listing['category_id'], listing_id)
    )
    similar_listings = cursor.fetchall()
        
    conn.close()
    return render_template('single_listing.html', listing=listing, similar=similar_listings)

@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            flash('Tizimga muvaffaqiyatli kirdingiz', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Login ko\'rsatkichlari noto\'g\'ri!', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Tizimdan chiqdingiz.', 'info')
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if request.method == 'POST':
        action = request.form.get('action')
        listing_id = request.form.get('listing_id')
            
        if action == 'delete' and listing_id:
            conn = get_db_connection()
            listing = conn.execute('SELECT image_filename FROM listings WHERE id = ?', (listing_id,)).fetchone()
            if listing and listing['image_filename']:
                img_path = os.path.join(app.config['UPLOAD_FOLDER'], listing['image_filename'])
                if os.path.exists(img_path):
                    try:
                        os.remove(img_path)
                    except:
                        pass
            conn.execute('DELETE FROM listings WHERE id = ?', (listing_id,))
            conn.commit()
            conn.close()
            flash('E\'lon o\'chirildi', 'success')
            
        elif action == 'toggle_top' and listing_id:
            conn = get_db_connection()
            conn.execute('UPDATE listings SET is_top = 1 - is_top WHERE id = ?', (listing_id,))
            conn.commit()
            conn.close()
            flash('E\'lon TOP holati yangilandi', 'success')

        elif action == 'toggle_pin' and listing_id:
            conn = get_db_connection()
            conn.execute('UPDATE listings SET is_pinned = 1 - is_pinned WHERE id = ?', (listing_id,))
            conn.commit()
            conn.close()
            flash('E\'lon PIN holati yangilandi', 'success')
            
        return redirect(url_for('admin_panel'))
        
    # Search + Filter
    q = request.args.get('q', '').strip()
    cat_filter = request.args.get('cat', '').strip()
    
    conn = get_db_connection()
    
    # Statistics
    stats = {}
    stats['total'] = conn.execute('SELECT COUNT(*) FROM listings').fetchone()[0]
    stats['today'] = conn.execute(
        "SELECT COUNT(*) FROM listings WHERE DATE(created_at) = DATE('now')"
    ).fetchone()[0]
    stats['top'] = conn.execute('SELECT COUNT(*) FROM listings WHERE is_top = 1').fetchone()[0]
    stats['pinned'] = conn.execute('SELECT COUNT(*) FROM listings WHERE is_pinned = 1').fetchone()[0]
    stats['categories'] = conn.execute('SELECT COUNT(*) FROM categories').fetchone()[0]

    # All banners for admin panel
    banners = conn.execute('SELECT * FROM banners ORDER BY created_at DESC').fetchall()

    
    # Build listing query with optional filters
    query = '''
        SELECT l.*, c.name as category_name 
        FROM listings l 
        JOIN categories c ON l.category_id = c.id 
        WHERE 1=1
    '''
    params = []
    if q:
        query += ' AND (l.title LIKE ? OR l.description LIKE ?)'
        params += ['%'+q+'%', '%'+q+'%']
    if cat_filter:
        query += ' AND c.slug = ?'
        params.append(cat_filter)
    query += ' ORDER BY l.created_at DESC'
    
    cur = conn.execute(query, params)
    listings = cur.fetchall()
    conn.close()
    return render_template('admin.html', listings=listings, stats=stats, banners=banners, q=q, cat_filter=cat_filter)


@app.route('/admin/edit/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def edit_listing(listing_id):
    conn = get_db_connection()
    listing = conn.execute('SELECT * FROM listings WHERE id = ?', (listing_id,)).fetchone()
    if listing is None:
        conn.close()
        abort(404)

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        category_id = request.form.get('category_id')
        contact_phone = request.form.get('contact_phone', '').strip()
        contact_telegram = request.form.get('contact_telegram', '').strip()
        if contact_telegram.startswith('@'):
            contact_telegram = contact_telegram[1:]

        try:
            price_val = float(price)
        except (ValueError, TypeError):
            flash('Narx formati noto\'g\'ri.', 'error')
            conn.close()
            return redirect(url_for('edit_listing', listing_id=listing_id))

        # Handle new image upload
        file = request.files.get('image')
        filename = listing['image_filename']  # keep old image by default
        if file and file.filename != '' and allowed_file(file.filename):
            # Delete old image if exists
            if filename:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(old_path):
                    try: os.remove(old_path)
                    except: pass
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn.execute(
            '''
            UPDATE listings SET title=?, description=?, price=?, category_id=?,
            contact_phone=?, contact_telegram=?, image_filename=? WHERE id=?
            ''',
            (title, description, price_val, category_id,
             contact_phone, contact_telegram, filename, listing_id)
        )
        conn.commit()
        conn.close()
        flash('E\'lon muvaffaqiyatli yangilandi!', 'success')
        return redirect(url_for('admin_panel'))

    conn.close()
    return render_template('edit_listing.html', listing=listing)


@app.route('/admin/banner/add', methods=['POST'])
@login_required
def add_banner():
    title = request.form.get('title', '').strip()
    link_url = request.form.get('link_url', '').strip()
    if not title:
        flash('Banner sarlavhasi kiritilishi shart.', 'error')
        return redirect(url_for('admin_panel') + '#banners')

    file = request.files.get('banner_image')
    filename = None
    if file and file.filename != '' and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"banner_{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO banners (title, image_filename, link_url) VALUES (?, ?, ?)',
        (title, filename, link_url)
    )
    conn.commit()
    conn.close()
    flash('Banner muvaffaqiyatli qo\'shildi!', 'success')
    return redirect(url_for('admin_panel') + '#banners')


@app.route('/admin/banner/delete/<int:banner_id>', methods=['POST'])
@login_required
def delete_banner(banner_id):
    conn = get_db_connection()
    banner = conn.execute('SELECT * FROM banners WHERE id = ?', (banner_id,)).fetchone()
    if banner and banner['image_filename']:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], banner['image_filename'])
        if os.path.exists(img_path):
            try: os.remove(img_path)
            except: pass
    conn.execute('DELETE FROM banners WHERE id = ?', (banner_id,))
    conn.commit()
    conn.close()
    flash('Banner o\'chirildi.', 'success')
    return redirect(url_for('admin_panel') + '#banners')


@app.route('/admin/banner/toggle/<int:banner_id>', methods=['POST'])
@login_required
def toggle_banner(banner_id):
    conn = get_db_connection()
    conn.execute('UPDATE banners SET is_active = 1 - is_active WHERE id = ?', (banner_id,))
    conn.commit()
    conn.close()
    flash('Banner holati yangilandi.', 'success')
    return redirect(url_for('admin_panel') + '#banners')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
