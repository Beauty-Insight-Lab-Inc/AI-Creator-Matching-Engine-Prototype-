import os
import pandas as pd
import joblib
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
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
    print(">>> [1/4] Fetching data from Database...")
    
    try:
        DB_URL = get_decrypted_db_url()
        engine = create_engine(DB_URL)
    except ValueError as e:
        print(f"Error initializing database connection: {e}")
        return

    # DB에서 학습 데이터 가져오기 (Matches + Creators 조인)
    # "누가(Creator) 어떤 성과(ROI)를 냈는가?"
    query = """
    SELECT 
        c.follower_count,
        c.niche,
        c.platform,
        m.actual_roi
    FROM matches m
    JOIN creators c ON m.creator_id = c.creator_id
    """
    df = pd.read_sql(query, engine)
    
    print(f"   Data loaded: {len(df)} records")
    print("   Features: follower_count, niche, platform")
    print("   Target: actual_roi")

    # 2. 데이터 분리 (Features vs Target)
    X = df[['follower_count', 'niche', 'platform']]
    y = df['actual_roi']

    # 학습셋/테스트셋 분리
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. 파이프라인 구축 (전처리 + 모델)
    print(">>> [2/4] Building ML Pipeline...")
    
    # 범주형 데이터(niche, platform)는 One-Hot Encoding, 수치형은 그대로
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['niche', 'platform']),
            ('num', 'passthrough', ['follower_count'])
        ]
    )

    # 모델: Random Forest (강력하고 범용적인 회귀 모델)
    model = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    # 4. 모델 학습
    print(">>> [3/4] Training the Model (Learning patterns)...")
    model.fit(X_train, y_train)

    # 5. 평가
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"   Model Performance -> MSE: {mse:.2f}, R2: {r2:.2f}")

    # 6. 모델 저장 (직렬화)
    print(">>> [4/4] Saving the Model...")
    save_path = '2_recommendation_model/saved_models/roi_predictor.joblib'
    joblib.dump(model, save_path)
    print(f"   Success! Model saved to: {save_path}")

if __name__ == "__main__":
    try:
        train_model()
    except Exception as e:
        print(f"Training Error: {e}")