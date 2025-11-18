import pandas as pd
import joblib
import os

# 저장된 모델 경로
MODEL_PATH = '2_recommendation_model/saved_models/roi_predictor.joblib'

# 모델 로드 (전역 변수로 한 번만 로드하여 속도 향상)
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None
    print("⚠️ 경고: 모델 파일이 없습니다. train.py를 먼저 실행하세요.")

def get_recommendations(target_budget, top_k=3):
    """
    입력된 예산(target_budget)으로 가능한 최적의 플랫폼과 인플루언서 조합을 추천합니다.
    """
    if model is None:
        return {"error": "Model not loaded"}

    # 1. 시뮬레이션할 후보군 정의 (우리가 가진 데이터의 범주들)
    # 실제 데이터에 있는 값들이어야 합니다.
    platforms = ['Instagram', 'YouTube', 'TikTok', 'Facebook'] 
    influencer_types = ['Nano', 'Micro', 'Macro', 'Mega']
    
    candidates = []

    # 2. 모든 조합 생성 (Grid Search 방식)
    for plat in platforms:
        for inf_type in influencer_types:
            candidates.append({
                'platform': plat,
                'influencer_category': inf_type,
                'budget': target_budget
            })
    
    # 데이터프레임으로 변환
    candidates_df = pd.DataFrame(candidates)

    # 3. AI 모델로 매출 예측
    predicted_sales = model.predict(candidates_df)
    
    # 4. 결과 정리 및 ROI 계산
    candidates_df['predicted_sales'] = predicted_sales
    
    # ROI 공식: ((매출 - 예산) / 예산) * 100
    candidates_df['predicted_roi'] = (
        (candidates_df['predicted_sales'] - candidates_df['budget']) 
        / candidates_df['budget'] * 100
    )

    # 5. ROI 높은 순으로 정렬 및 Top K 추출
    top_recommendations = candidates_df.sort_values(
        by='predicted_roi', ascending=False
    ).head(top_k)

    # JSON 형태로 변환하여 반환
    return top_recommendations.to_dict(orient='records')

# 테스트용 코드 (이 파일을 직접 실행할 때만 작동)
if __name__ == "__main__":
    budget = 5000 # 5000달러 예산
    results = get_recommendations(budget)
    print(f"💰 예산 ${budget}일 때 AI 추천 전략 TOP 3:")
    for i, rec in enumerate(results, 1):
        print(f"{i}. [{rec['platform']} - {rec['influencer_category']}] 예상 ROI: {rec['predicted_roi']:.1f}%")