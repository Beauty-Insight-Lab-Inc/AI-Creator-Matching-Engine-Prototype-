import pandas as pd
from sqlalchemy import create_engine, text
import os
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


def load_full_data():
    print("🔄 [15만 개] 전체 데이터 로딩 및 DB 적재 시작...")
    
    # 1. CSV 파일 읽기
    # 파일명이 정확한지 확인해주세요 (폴더 위치 등)
    csv_file = '1_data_simulation\influencer_marketing_roi_dataset.csv' # ⚠️ 전체 데이터 파일명으로 수정 필요!
    
    # 혹시 파일이 없으면 에러 처리
    if not os.path.exists(csv_file):
        # Kaggle 데이터셋 파일명이 다를 수 있으니 확인용
        print(f"❌ 파일을 찾을 수 없습니다: {csv_file}")
        return

    df = pd.read_csv(csv_file)

    # 2. 가상 예산(Budget) 생성 (도달수 기반)
    print("💰 가상 예산 데이터 생성 중...")
    df['budget'] = df['estimated_reach'] * 0.03 
    df['budget'] = df['budget'].astype(int)

    # 3. 컬럼명 정리
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

    # 필요한 컬럼만 선택
    target_columns = [
        'campaign_id', 'platform', 'influencer_category', 'campaign_type',
        'start_date', 'engagements', 'estimated_reach', 'product_sales',
        'budget', 'campaign_duration_days', 'end_date'
    ]
    df = df[target_columns]

    # 4. DB에 밀어넣기
    try:
        DB_URL = get_decrypted_db_url()
        engine = create_engine(DB_URL)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)

    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS campaign_performance CASCADE;"))
        print("🗑️ 기존(테스트) 테이블 삭제 완료")
        
        # 청크 단위로 나누어 넣으면 더 안정적일 수 있음 (chunksize 옵션)
        df.to_sql('campaign_performance', conn, if_exists='replace', index=False)
        print(f"✅ {len(df)}개 데이터 적재 완료! (이제 eda.py를 실행해보세요)")

if __name__ == "__main__":
    load_full_data()