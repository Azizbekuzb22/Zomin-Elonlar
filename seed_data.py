"""
Zomin E'lonlar - Fake e'lonlar qo'shish scripti
"""
import sqlite3
import os
from datetime import datetime, timedelta
import random

db_path = os.path.join(os.path.dirname(__file__), 'zomin_market.db')

listings = [
    {
        "title": "Chevrolet Cobalt 2022 yil, oq rang",
        "description": "Mashina juda yaxshi holatda. Bitta egasi. Hech qanday qoqish-urishi yo'q. Polisi bor, yillik TO o'tgan. Muloqot qilish uchun qo'ng'iroq qiling.",
        "price": 135000000,
        "category": "Avtomobillar",
        "phone": "+998 93 456 78 90",
        "telegram": "cobalt2022_zomin",
        "condition": "Ishlatilgan (A'lo)",
        "views": random.randint(50, 300),
        "days_ago": 1,
    },
    {
        "title": "iPhone 13 Pro Max 256GB, Tog' ko'ki",
        "description": "Telefon 10/10 holatda. Batareya salomatligi 94%. Original zaryadlovchi va quticha bor. Hech qachon tushirilmagan. Almashtirmayman.",
        "price": 9800000,
        "category": "Elektronika",
        "phone": "+998 90 123 45 67",
        "telegram": "iphone_zomin",
        "condition": "Ishlatilgan (A'lo)",
        "views": random.randint(80, 500),
        "days_ago": 0,
    },
    {
        "title": "3 xonali uy, Zomin shahri markazida",
        "description": "Uy 2019 yilda qurilgan. 120 kv.m. Suv, gaz, elektr bor. Hovli 5 sotix. Garaj va omborxona mavjud. Narx kelishiladi.",
        "price": 280000000,
        "category": "Ko'chmas mulk",
        "phone": "+998 91 234 56 78",
        "telegram": "uy_zomin_markazda",
        "condition": "Noma'lum",
        "views": random.randint(100, 600),
        "days_ago": 2,
    },
    {
        "title": "Samsung Galaxy S23 Ultra 256GB",
        "description": "Telefon yangi, qutida, barcha jihozlari bilan. Chegirma qilinmaydi. Xaqiqiy, original tovar.",
        "price": 11500000,
        "category": "Elektronika",
        "phone": "+998 97 567 89 01",
        "telegram": "samsung_s23_zomin",
        "condition": "Yangi",
        "views": random.randint(40, 200),
        "days_ago": 0,
    },
    {
        "title": "Daewoo Nexia 2, 2011 yil",
        "description": "Motori yangilangan. Gaz (metan) o'rnatilgan. Hujjatlari tamom. Yillik texosmotr o'tgan. Egar olib beriladi.",
        "price": 38000000,
        "category": "Avtomobillar",
        "phone": "+998 93 789 01 23",
        "telegram": "nexia2_zomin",
        "condition": "Ishlatilgan",
        "views": random.randint(30, 150),
        "days_ago": 3,
    },
    {
        "title": "Erkaklar uchun Nike Air Max sneaker, 42 o'lcham",
        "description": "Butunlay yangi, qutida. Dubay'dan keltirilgan. Original mahsulot. Boshqa o'lchamlar ham bor, so'rang.",
        "price": 850000,
        "category": "Kiyim-kechak",
        "phone": "+998 94 321 87 65",
        "telegram": "nike_zomin",
        "condition": "Yangi",
        "views": random.randint(20, 120),
        "days_ago": 1,
    },
    {
        "title": "Duradgor ustasi - mebel va eshik tayyorlash",
        "description": "10 yillik tajribam bor. Har qanday mebel, shkaf, eshik, derazalar tayyorlayman. Sifatli va arzon. Zomin va atroflarga chiqaman.",
        "price": 150000,
        "category": "Ish o'rinlari",
        "phone": "+998 90 987 65 43",
        "telegram": "duradgor_zomin",
        "condition": "Noma'lum",
        "views": random.randint(15, 100),
        "days_ago": 4,
    },
    {
        "title": "LG 55 dyuymli Smart TV, 4K UHD",
        "description": "2 yil ishlatilgan, ekranda hech qanday darz yo'q. Android 11 OS. YouTube, Netflix ishlaydi. Uy sharoiti uchun ideal.",
        "price": 3200000,
        "category": "Elektronika",
        "phone": "+998 91 111 22 33",
        "telegram": "lg_tv_zomin",
        "condition": "Ishlatilgan (A'lo)",
        "views": random.randint(25, 180),
        "days_ago": 2,
    },
    {
        "title": "2 xonali kvartira ijaraga, Zomin",
        "description": "2-qavat, lift bor. Yangi ta'mirlangan. Hamma narsa yangi. Oilaviy juftliklar uchun mos. Kommunal alohida. Garov talab qilinmaydi.",
        "price": 1800000,
        "category": "Ko'chmas mulk",
        "phone": "+998 93 444 55 66",
        "telegram": "kvartira_ijara_zomin",
        "condition": "Noma'lum",
        "views": random.randint(60, 400),
        "days_ago": 0,
    },
    {
        "title": "Adidas original sport kiyim to'plami (erkaklar)",
        "description": "Trening va futbolka. L o'lcham. Haqiqiy original mahsulot, Toshkentdan keltirilgan. Yuvishda shakli o'zgarmaydi.",
        "price": 450000,
        "category": "Kiyim-kechak",
        "phone": "+998 99 777 88 99",
        "telegram": "adidas_zomin",
        "condition": "Yangi",
        "views": random.randint(10, 80),
        "days_ago": 1,
    },
]

def seed():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Get categories
    cats = conn.execute("SELECT id, name FROM categories").fetchall()
    cat_map = {c['name']: c['id'] for c in cats}
    
    added = 0
    for l in listings:
        cat_id = cat_map.get(l['category'])
        if not cat_id:
            print(f"Kategoriya topilmadi: {l['category']}")
            continue
        
        created = datetime.now() - timedelta(days=l['days_ago'], hours=random.randint(0, 8))
        
        try:
            conn.execute('''
                INSERT INTO listings 
                (title, description, price, category_id, condition, contact_phone, contact_telegram, views, created_at, is_top, is_pinned)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
            ''', (
                l['title'], l['description'], l['price'], cat_id,
                l['condition'], l['phone'], l['telegram'],
                l['views'], created.strftime('%Y-%m-%d %H:%M:%S')
            ))
            added += 1
            print(f"✅ Qo'shildi: {l['title'][:40]}")
        except Exception as e:
            print(f"❌ Xato: {e}")

    conn.commit()
    conn.close()
    print(f"\n🎉 Jami {added} ta e'lon muvaffaqiyatli qo'shildi!")

if __name__ == '__main__':
    seed()
