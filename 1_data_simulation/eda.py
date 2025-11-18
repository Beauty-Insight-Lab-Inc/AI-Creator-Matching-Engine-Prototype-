import pandas as pd
from sqlalchemy import create_engine
import os
import seaborn as sns
import matplotlib.pyplot as plt
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

def run_eda_basic():
    print("📊 데이터 로딩 중...")
    query = "SELECT * FROM campaign_performance"
    df = pd.read_sql(query, engine)
    
    # --- 🔍 DEBUGGING START ---
    print(f"\n🧐 Loaded {len(df)} rows.")
    print("📋 Actual Columns in DB:", df.columns.tolist())
    
    if 'budget' not in df.columns:
        print("❌ ERROR: 'budget' column is MISSING.")
        print("   Possible fixes:")
        print("   1. Check if DB_URL in this file matches add_budget.py exactly.")
        print("   2. Re-run add_budget.py to ensure the table was updated.")
        return
    # --- 🔍 DEBUGGING END ---

    # 1. ROI Calculation
    df['calculated_roi'] = df.apply(
        lambda x: ((x['product_sales'] - x['budget']) / x['budget'] * 100) if x['budget'] > 0 else 0, 
        axis=1
    )

    # 2. Data Info
    print("\n[1. Data Info]")
    print(df.info())

    # 3. Basic Statistics
    print("\n[2. Basic Statistics]")
    print(df[['budget', 'product_sales', 'estimated_reach', 'calculated_roi']].describe().round(2))

    # 4. Correlation Heatmap (Visual check)
    plt.figure(figsize=(10, 8))
    # Select only numeric columns for correlation
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("KPI Correlation Heatmap")
    plt.show()

    return df

if __name__ == "__main__":
    run_eda_basic()