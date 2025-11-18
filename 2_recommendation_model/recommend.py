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

# DB 및 데이터 로드
try:
    DB_URL = get_decrypted_db_url()
    engine = create_engine(DB_URL)
except ValueError as e:
    print(f"Error: {e}")
    exit(1)
df = pd.read_sql('SELECT * FROM campaign_performance', engine)

def recommend_influencers(
    campaign_type=None,
    influencer_category=None,
    platform=None,
    top_n=10,
    min_product_sales=0,
    min_engagements=0
):
    # 1. 캠페인 조건 기반 필터링
    filtered = df.copy()
    if campaign_type:
        filtered = filtered[filtered['campaign_type'] == campaign_type]
    if influencer_category:
        filtered = filtered[filtered['influencer_category'] == influencer_category]
    if platform:
        filtered = filtered[filtered['platform'] == platform]
    filtered = filtered[
        (filtered['product_sales'] >= min_product_sales) &
        (filtered['engagements'] >= min_engagements)
    ]
    # 2. 점수 산식
    filtered['score'] = (
        0.4 * filtered['engagements'].fillna(0)
        + 0.3 * filtered['estimated_reach'].fillna(0)
        + 0.3 * filtered['product_sales'].fillna(0)
    )
    # 3. TOP N 인플루언서 반환
    return filtered.sort_values(by='score', ascending=False).head(top_n)

# 테스트 실행 예시
result = recommend_influencers(
    campaign_type='Brand Awareness',
    influencer_category='Food',
    platform='YouTube',
    top_n=5,
    min_product_sales=100
)
print(result[['campaign_id','platform','influencer_category','score']])
