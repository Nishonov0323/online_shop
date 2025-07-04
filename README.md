# Online Shop 🛒

Python-da yaratilgan zamonaviy online do'kon ilovasi.

## 📋 Loyiha haqida

Bu loyiha Python tilida yozilgan online do'kon veb-ilovasi bo'lib, foydalanuvchilarga qulay xarid qilish imkoniyatini taqdim etadi.

## 🚀 Xususiyatlar

- **Mahsulotlar katalogi** - Turli kategoriyalardagi mahsulotlarni ko'rish
- **Foydalanuvchi ro'yxatdan o'tishi** - Xavfsiz autentifikatsiya tizimi
- **Savatcha funksiyasi** - Mahsulotlarni savatga qo'shish va boshqarish
- **To'lov tizimi** - Xavfsiz onlayn to'lovlar
- **Admin panel** - Mahsulotlar va buyurtmalarni boshqarish
- **Qidiruv** - Mahsulotlarni qidirish va filtrlash

## 🛠️ Texnologiyalar

- **Backend**: Python
- **Framework**: Django
- **Ma'lumotlar bazasi**: PostgreSQL
- **Frontend**: Telegram bot interfeysi

## 📦 O'rnatish

### Talablar

- Python 3.12+
- pip
- virtualenv (tavsiya etiladi)

### O'rnatish qadamlari

1. **Repository ni klonlash**
```bash
  git clone https://github.com/Nishonov0323/online_shop.git
  cd online_shop
```

2. **Virtual muhit yaratish**
```bash
  python -m venv venv
  source venv/bin/activate  # Linux/Mac
# yoki
  venv\Scripts\activate  # Windows
```

3. **Kerakli kutubxonalarni o'rnatish**
```bash
  pip install -r requirements.txt
```

4. **Ma'lumotlar bazasini sozlash**
```bash
  python manage.py makemigrations
  python manage.py migrate
```

5. **Superuser yaratish**
```bash
  python manage.py createsuperuser
```

6. **Serverni ishga tushirish**
```bash
  python manage.py runserver
```

## 🖥️ Foydalanish

1. Brauzeringizda `http://localhost:8000` manzilini oching
2. Foydalanuvchi sifatida ro'yxatdan o'ting yoki tizimga kiring
3. Mahsulotlarni ko'ring va savatga qo'shing
4. Xaridni yakunlang

### Admin panel

Admin panelga kirish uchun: `http://localhost:8000/admin`


## 🔧 Sozlash

### Environment o'zgaruvchilari

`.env` fayl yarating va quyidagi o'zgaruvchilarni qo'shing:

```env
SECRET_KEY="django_secret_key"
DEBUG=True

DB_NAME=database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432

TELEGRAM_TOKEN="your_telegram_bot_token"

BASE_URL=http://127.0.0.1:8000
```

## 🤝 Hissa qo'shish

1. Repository ni fork qiling
2. Yangi branch yarating (`git checkout -b feature/AmazingFeature`)
3. O'zgarishlaringizni commit qiling (`git commit -m 'Add some AmazingFeature'`)
4. Branch ga push qiling (`git push origin feature/AmazingFeature`)
5. Pull Request yarating

## 📝 Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi. Batafsil ma'lumot uchun `LICENSE` faylini ko'ring.

## 👨‍💻 Muallif

**Nishonov0323**
- GitHub: [@Nishonov0323](https://github.com/Nishonov0323)

## 📞 Aloqa

Savollar yoki takliflar bo'lsa, GitHub Issues orqali murojaat qiling.

## 🔄 Oxirgi yangilanishlar

- **v1.0.0** - Asosiy funksiyalar qo'shildi
- Mahsulotlar katalogi
- Foydalanuvchi ro'yxatdan o'tishi
- Savatcha tizimi

---

⭐ Agar bu loyiha sizga yoqsa, yulduzcha bering!