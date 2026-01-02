

---

# 🎬 Movie Rating System

سیستمی برای مدیریت فیلم‌ها و ثبت امتیاز، پیاده‌سازی‌شده با **FastAPI**, **PostgreSQL**, و **Docker**.

این پروژه در سه فاز طراحی شده است:

1️⃣ پیاده‌سازی API
2️⃣ افزودن سیستم Logging
3️⃣ اجرای پروژه با Docker & Docker Compose

---

## 📂 ساختار پروژه

```
app/
 ├── main.py
 ├── core/
 ├── db/
 ├── models/
 ├── schemas/
 ├── repositories/
 ├── services/
 └── controller/
Dockerfile
docker-compose.yml
requirements.txt
```

### توضیح کوتاه

| پوشه / فایل          | نقش                                |
| -------------------- | ---------------------------------- |
| `app/main.py`        | نقطه‌ی ورود برنامه و تعریف FastAPI |
| `core/`              | تنظیمات، logging، decorators       |
| `db/`                | اتصال به دیتابیس و session         |
| `models/`            | مدل‌های دیتابیس (SQLAlchemy)       |
| `schemas/`           | مدل‌های ورودی/خروجی (Pydantic)     |
| `repositories/`      | کوئری‌ها و کار با دیتابیس          |
| `services/`          | منطق بیزنسی                        |
| `controller/`        | تعریف endpointها و API             |
| `Dockerfile`         | ساخت image اپلیکیشن                |
| `docker-compose.yml` | اجرای app + db با هم               |

---

## 🚀 نحوه اجرا

### ✔️ روش ۱ — با Docker (توصیه‌شده)

پیش‌نیاز:
Docker و Docker Compose نصب باشند.

سپس:

```bash
docker compose up --build
```

سرویس‌ها بالا می‌آیند:

* API → روی پورت **8000**
* دیتابیس → روی پورت **5432**

Swagger Docs:

```
http://localhost:8000/docs
```

---

### ✔️ روش ۲ — اجرای لوکال (فاز ۱ و ۲)

پیش‌نیاز:

* Python 3.12+
* PostgreSQL

۱) نصب وابستگی‌ها:

```bash
pip install -r requirements.txt
```

۲) تنظیم متغیر محیطی:

```
DATABASE_URL=postgresql://user:password@localhost:5432/moviedb
```

۳) اجرا:

```bash
uvicorn app.main:app --reload
```

---

## 🎯 امکانات اصلی

### 🎥 مدیریت فیلم‌ها (CRUD)

| متد    | مسیر                  | توضیح                     |
| ------ | --------------------- | ------------------------- |
| GET    | `/api/v1/movies`      | لیست با فیلتر و صفحه‌بندی |
| GET    | `/api/v1/movies/{id}` | جزئیات فیلم               |
| POST   | `/api/v1/movies`      | ساخت فیلم جدید            |
| PUT    | `/api/v1/movies/{id}` | ویرایش                    |
| DELETE | `/api/v1/movies/{id}` | حذف                       |

### 🔎 فیلترها

* عنوان (title)
* سال انتشار (release_year)
* ژانر (genre)
* صفحه‌بندی (page / page_size)

### ⭐ ثبت امتیاز

| متد  | مسیر                          |
| ---- | ----------------------------- |
| POST | `/api/v1/movies/{id}/ratings` |

ذخیره:

* score
* محاسبه‌ی میانگین
* تعداد امتیازها

---

## 📝 قالب پاسخ‌ها

### ✔️ موفق

```json
{
  "status": "success",
  "data": { ... }
}
```

### ❌ خطا

```json
{
  "status": "failure",
  "error": {
    "code": 404,
    "message": "Movie not found"
  }
}
```

---

## 📒 Logging (Phase 2)

برای هر درخواست ثبت می‌شود:

* شروع پردازش
* پارامترها
* نتیجه
* مدت زمان اجرا
* خطاها / هشدارها

نمونه:

```
list_movies - started
Movies listed successfully (page=1, page_size=10)
list_movies - finished in 52 ms
```

خطای 404:

```
WARNING - Movie not found
```

---

## 🐳 Docker (Phase 3)

### docker-compose

* سرویس **db** → Postgres
* سرویس **app** → FastAPI

اتصال داخلی:

```
postgresql://movie_user:movie_password@db:5432/moviedb
```

داده‌ها در volume ذخیره می‌شوند تا با ریست، پاک نشوند.

---

## 🔐 Environment Variables

نمونه:

```
DATABASE_URL=postgresql://movie_user:movie_password@db:5432/moviedb
APP_ENV=production
```

هدف:

* امنیت بیشتر
* تغییر تنظیمات بدون ویرایش کد

---

## 🧠 مفاهیم مهم

* REST API
* Status Codes (200 / 201 / 404 / 422 / 500)
* Validation با Pydantic
* ORM با SQLAlchemy
* لایه‌بندی: Controller → Service → Repository
* Logging برای Debug
* Docker & Compose برای اجرای استاندارد

---


