CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    icon TEXT
);

CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    category_id INTEGER,
    contact_phone TEXT,
    contact_telegram TEXT,
    image_filename TEXT,
    is_top BOOLEAN DEFAULT 0,
    is_pinned BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories (id)
);

CREATE TABLE IF NOT EXISTS banners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    image_filename TEXT,
    link_url TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO categories (name, slug, icon) VALUES 
('Avtomobillar', 'avtomobillar', '🚗'),
('Elektronika', 'elektronika', '📱'),
('Kiyim-kechak', 'kiyim-kechak', '👕'),
('Ko''chmas mulk', 'kochmas-mulk', '🏠'),
('Ish o''rinlari', 'ish-orinlari', '💼'),
('Boshqalar', 'boshqalar', '📦');

