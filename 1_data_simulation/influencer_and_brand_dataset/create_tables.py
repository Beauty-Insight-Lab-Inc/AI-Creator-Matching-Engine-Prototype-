import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from cryptography.fernet import Fernet

def get_decrypted_db_url():
    """환경변수에서 암호화된 DB URL을 복호화하여 반환합니다."""
    key = os.getenv("ENCRYPTION_KEY")
    encrypted_url = os.getenv("ENCRYPTED_DATABASE_URL")

    if not key or not encrypted_url:
        # fallback to the old plain text DATABASE_URL for backward compatibility
        plain_db_url = os.getenv("DATABASE_URL")
        if plain_db_url:
            print("Warning: Using plain text DATABASE_URL. For better security, please use ENCRYPTION_KEY and ENCRYPTED_DATABASE_URL.")
            return plain_db_url
        raise ValueError("ENCRYPTION_KEY and ENCRYPTED_DATABASE_URL must be set, or a plain DATABASE_URL must be provided.")

    try:
        f = Fernet(key.encode('utf-8'))
        decrypted_url = f.decrypt(encrypted_url.encode('utf-8')).decode('utf-8')
        return decrypted_url
    except Exception as e:
        raise ValueError(f"Failed to decrypt DATABASE_URL. Check your key and encrypted URL. Error: {e}")

# .env 파일에서 환경변수 로드
load_dotenv()

# 복호화된 DB URL을 사용하여 엔진 생성
try:
    DB_URL = get_decrypted_db_url()
    engine = create_engine(DB_URL)
except ValueError as e:
    print(f"Error: {e}")
    exit(1)

def init_db():
    with engine.connect() as conn:
        # 1. 기존 테이블이 있다면 삭제 (초기화) - 주의: 데이터가 날아갑니다.
        conn.execute(text("DROP TABLE IF EXISTS matches CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS campaigns CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS creators CASCADE;"))
        
        # 2. Creators 테이블 생성
        conn.execute(text("""
            CREATE TABLE creators (
                creator_id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                follower_count INTEGER,
                niche VARCHAR(100),
                platform VARCHAR(50),
                bio TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # 3. Campaigns 테이블 생성
        conn.execute(text("""
            CREATE TABLE campaigns (
                campaign_id SERIAL PRIMARY KEY,
                brand_name VARCHAR(255),
                product_category VARCHAR(100),
                budget INTEGER,
                content_requirements TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # 4. Matches 테이블 생성
        conn.execute(text("""
            CREATE TABLE matches (
                match_id SERIAL PRIMARY KEY,
                creator_id INTEGER REFERENCES creators(creator_id),
                match_method VARCHAR(50),
                actual_roi FLOAT,
                outcome VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        conn.commit()
        print(">>> Database tables created successfully.")

if __name__ == "__main__":
    try:
        init_db()
    except Exception as e:
        print(f"Error creating tables: {e}")