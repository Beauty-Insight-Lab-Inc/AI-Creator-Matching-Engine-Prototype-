import pandas as pd
import joblib
import os
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
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

def train_model():
    print("🚀 모델 학습 데이터 로딩 중...")
    try:
        DB_URL = get_decrypted_db_url()
        engine = create_engine(DB_URL)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    
    # 수정된 컬럼명으로 쿼리 (influencer_category 사용)
    query = """
    SELECT 
        platform, 
        influencer_category, 
        budget, 
        product_sales 
    FROM campaign_performance
    """
    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        print(f"❌ DB 에러: {e}")
        return

    if df.empty:
        print("❌ 데이터가 없습니다. etl_load.py를 먼저 실행하세요.")
        return

    # 1. 입력(X)과 정답(y) 분리
    X = df[['platform', 'influencer_category', 'budget']]
    y = df['product_sales']

    # 2. 전처리 파이프라인
    # 범주형 데이터(문자열) -> 수치형 변환
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['platform', 'influencer_category'])
        ],
        remainder='passthrough'
    )

    # 3. 모델 정의 (Random Forest)
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    # 4. 학습 진행
    print("🧠 AI 학습 시작...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model_pipeline.fit(X_train, y_train)

    # 성능 평가
    score = model_pipeline.score(X_test, y_test)
    print(f"✅ 학습 완료! 예측 정확도(R2 Score): {score:.2f}")

    # 5. 모델 저장
    os.makedirs('2_recommendation_model/saved_models', exist_ok=True)
    save_path = '2_recommendation_model/saved_models/roi_predictor.joblib'
    joblib.dump(model_pipeline, save_path)
    print(f"💾 모델 파일 저장됨: {save_path}")

if __name__ == "__main__":
    train_model()