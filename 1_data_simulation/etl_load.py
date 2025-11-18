# 0)  pip install pandas sqlalchemy psycopg2 python-dotenv cryptography
import pandas as pd
import os
from sqlalchemy import create_engine
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

# 1) Kaggle CSV 다운로드, 경로 확인
df = pd.read_csv('1_data_simulation\influencer_marketing_roi_dataset.csv')

# 2) 필요한 컬럼명만 맞추기(최소한 위 CREATE TABLE 구조에 맞게)
df = df.rename(columns={
    'campaign_id': 'campaign_id',
    'platform': 'platform',
    'influencer_category': 'influencer_category',
    'campaign_type': 'campaign_type',
    'start_date': 'start_date',
    'engagements': 'engagements',
    'estimated_reach': 'estimated_reach',
    'product_sales': 'product_sales',
    'budget': 'budget',
    'campaign_duration_days': 'campaign_duration_days',
    'end_date': 'end_date'
})

# 3) DB 연결 (SQLAlchemy)
try:
    DB_URL = get_decrypted_db_url()
    engine = create_engine(DB_URL)
except ValueError as e:
    print(f"Error: {e}")
    exit(1)

# 4) 데이터 적재
df.to_sql('campaign_performance', engine, if_exists='append', index=False)
print("데이터 적재 완료")
