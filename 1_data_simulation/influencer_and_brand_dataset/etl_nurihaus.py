import pandas as pd
import os
import random # 가상 ROI 생성을 위해 추가
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# ==========================================
# 1. 설정 및 DB 연결
# ==========================================

# .env 파일에서 환경변수 로드
load_dotenv()

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


# 복호화된 DB URL을 사용하여 엔진 생성
try:
    DB_URL = get_decrypted_db_url()
    engine = create_engine(DB_URL)
except ValueError as e:
    print(f"Error: {e}")
    # DB URL을 얻지 못하면 스크립트를 더 이상 진행할 수 없으므로 종료
    exit(1)

# 경로 설정: 스크립트의 위치를 기준으로 절대 경로를 생성합니다.
# 이렇게 하면 어떤 경로에서 스크립트를 실행하더라도 데이터 폴더를 정확히 찾을 수 있습니다.
script_dir = os.path.dirname(os.path.abspath(__file__))
DIR_INFLUENCERS = os.path.join(script_dir, 'users_influencers_SPOD')
DIR_BRANDS = os.path.join(script_dir, 'users_brands_SPOD')
FILE_POST_INFO = os.path.join(script_dir, 'post_info.txt')

# K-뷰티 필터링 키워드
BEAUTY_KEYWORDS = ['beauty', 'skin', 'makeup', 'cosmetic', 'kbeauty', 'mask', 'care', 'daily', 'style']

def get_db_connection():
    return engine.connect()

def clear_tables():
    """Deletes all data from the target tables to ensure a fresh start."""
    print(">>> Clearing existing data from tables...")
    with get_db_connection() as connection:
        with connection.begin(): # 트랜잭션 시작
            connection.execute(text("DELETE FROM matches;"))
            connection.execute(text("DELETE FROM campaigns;"))
            connection.execute(text("DELETE FROM creators;"))
    print("   Success: Tables cleared.")

# ==========================================
# 2. Creators 테이블 적재 (폴더 내 txt 파일 순회)
# ==========================================
def load_creators():
    print(f">>> [1/3] Loading Creators from {DIR_INFLUENCERS}...")
    
    data = []
    # 해당 디렉토리의 모든 파일을 가져옵니다.
    try:
        file_list = [os.path.join(DIR_INFLUENCERS, f) for f in os.listdir(DIR_INFLUENCERS) if os.path.isfile(os.path.join(DIR_INFLUENCERS, f))]
    except FileNotFoundError:
        print(f"   Error: Directory not found at {DIR_INFLUENCERS}")
        return

    # 최대 5000개만 처리하여 속도 향상
    file_list = file_list[:5000]
    
    for file_path in file_list:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # 탭으로 분리된 첫 줄 읽기
                line = f.readline().strip().split('\t')
                if len(line) < 8: continue

                username = line[0]
                if not username: continue # username이 비어있으면 건너뛰기

                followers = int(line[1]) if line[1].isdigit() else 0
                bio = line[7]
                
                # 뷰티 관련 키워드 필터링
                if any(keyword in bio.lower() for keyword in BEAUTY_KEYWORDS):
                    data.append({
                        'username': username,
                        'follower_count': followers,
                        'niche': 'Beauty',
                        'platform': 'Instagram',
                        'bio': bio[:500]
                    })
        except Exception:
            continue

    if not data:
        print("   Warning: No creators loaded.")
        return

    df_creators = pd.DataFrame(data)
    # 중복된 username 제거 (첫 번째 항목 유지)
    df_creators.drop_duplicates(subset=['username'], keep='first', inplace=True)
    
    # DB 적재
    df_creators.to_sql('creators', engine, if_exists='append', index=False, method='multi')
    print(f"   Success: {len(df_creators)} beauty creators loaded.")

# ==========================================
# 3. Campaigns 테이블 적재 (폴더 내 txt 파일 순회)
# ==========================================
def load_campaigns():
    print(f">>> [2/3] Loading Campaigns from {DIR_BRANDS}...")
    
    data = []
    # 해당 디렉토리의 모든 파일을 가져옵니다.
    try:
        file_list = [os.path.join(DIR_BRANDS, f) for f in os.listdir(DIR_BRANDS) if os.path.isfile(os.path.join(DIR_BRANDS, f))]
    except FileNotFoundError:
        print(f"   Error: Directory not found at {DIR_BRANDS}")
        return

    # 최대 2000개만 처리하여 속도 향상
    file_list = file_list[:2000]
    
    for file_path in file_list:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                line = f.readline().strip().split('\t')
                if len(line) < 8: continue
                
                brand_name = line[0]
                if not brand_name: continue # brand_name이 비어있으면 건너뛰기
                
                bio = line[7]
                
                if any(keyword in bio.lower() for keyword in BEAUTY_KEYWORDS):
                    data.append({
                        'brand_name': brand_name,
                        'product_category': 'Beauty/Skincare',
                        'budget': random.randint(1000, 10000), # 데모용 가상 예산 ($1k~$10k)
                        'content_requirements': bio[:200]
                    })
        except Exception:
            continue
                    
    df_campaigns = pd.DataFrame(data)
    if not df_campaigns.empty:
        # 중복된 brand_name 제거 (첫 번째 항목 유지)
        df_campaigns.drop_duplicates(subset=['brand_name'], keep='first', inplace=True)
        df_campaigns.to_sql('campaigns', engine, if_exists='append', index=False, method='multi')
        print(f"   Success: {len(df_campaigns)} beauty brands loaded.")

# ==========================================
# 4. Matches 테이블 적재 (post_info.txt)
# ==========================================
def load_matches():
    print(f">>> [3/3] Loading Matches from {FILE_POST_INFO}...")
    
    # post_info.txt 읽기 (헤더 없음)
    try:
        df_posts = pd.read_csv(FILE_POST_INFO, sep='\t', header=None, usecols=[0, 1, 2],
                               names=['post_id', 'username', 'is_sponsored'])
    except Exception as e:
        print(f"   Error reading {FILE_POST_INFO}: {e}")
        return

    # 스폰서십(광고)인 게시물만 필터링 (Label == 1)
    sponsored_posts = df_posts[df_posts['is_sponsored'] == 1].copy()
    
    # PoC 데이터 제한 (2000개만)
    sponsored_posts = sponsored_posts.head(2000)
    
    matches_data = []
    
    print("   Generating synthetic ROI for sponsored posts...")
    for _, row in sponsored_posts.iterrows():
        synthetic_roi = round(random.uniform(5.0, 15.0), 1)
        matches_data.append({
            'match_method': 'Synthetic_Random', # 매칭 방식 변경 명시
            'actual_roi': synthetic_roi,
            'outcome': 'Completed'
            # temp_username은 더 이상 필요 없음
        })

    if matches_data:
        df_matches = pd.DataFrame(matches_data)
        
        # [수정된 로직]
        # 1. DB에서 방금 로드한 크리에이터 목록(ID) 가져오기
        existing_creators = pd.read_sql("SELECT creator_id FROM creators", engine)
        
        if existing_creators.empty:
            print("   Warning: No creators found in DB. Cannot create synthetic matches.")
            return

        # 2. 로드된 크리에이터에게 스폰서십 성과(ROI)를 랜덤으로 할당
        print("   Assigning synthetic ROI to random creators...")
        creator_ids = existing_creators['creator_id'].tolist()
        
        # 생성된 매칭 데이터 개수만큼 랜덤으로 creator_id를 복원추출하여 할당
        df_matches['creator_id'] = np.random.choice(creator_ids, size=len(df_matches), replace=True)

        # 3. 필요한 컬럼만 선택하여 적재
        db_ready_df = df_matches[['creator_id', 'match_method', 'actual_roi', 'outcome']]
        
        db_ready_df.to_sql('matches', engine, if_exists='append', index=False, method='multi')
        print(f"   Success: {len(db_ready_df)} synthetic matches randomly assigned and loaded.")

if __name__ == "__main__":
    try:
        clear_tables()
        load_creators()
        load_campaigns()
        load_matches()
        print("\n>>> ETL Process Completed Successfully.")
    except Exception as e:
        print(f"\n>>> ETL Error: {e}")