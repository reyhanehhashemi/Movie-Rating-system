# scripts/seed_check.py

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import get_settings  # استفاده از همان تنظیمات اپ

settings = get_settings()

# دقیقا همان DATABASE_URL که اپلیکیشن FastAPI استفاده می‌کند
engine = create_engine(settings.DATABASE_URL, future=True)


def verify_seeding() -> None:
    try:
        with Session(engine) as session:
            movie_count = session.execute(
                text("SELECT COUNT(*) FROM movies")
            ).scalar_one()

            director_count = session.execute(
                text("SELECT COUNT(*) FROM directors")
            ).scalar_one()

            rating_count = session.execute(
                text("SELECT COUNT(*) FROM movie_ratings")
            ).scalar_one()

            print("🎬 Movies      :", movie_count)
            print("🎭 Directors   :", director_count)
            print("⭐ Ratings rows:", rating_count)

            if movie_count == 1000 and director_count > 0:
                print("\n✅ Seeding looks SUCCESSFUL (1000 movies present).")
            else:
                print("\n⚠️ Seeding might be incomplete or modified.")

    except Exception as e:
        print("Error verifying seeding:", e)


if __name__ == "__main__":
    verify_seeding()
