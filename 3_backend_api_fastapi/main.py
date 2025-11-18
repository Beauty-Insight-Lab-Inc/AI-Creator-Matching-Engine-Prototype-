import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

# 1. FastAPI 앱 초기화
app = FastAPI(title="Nurihaus PoC AI API", description="Creator Matching & ROI Prediction")

# 2. 학습된 모델 로드 (서버 시작 시 한 번만 로드)
# 주의: train.py에서 저장한 경로와 일치해야 함
MODEL_PATH = os.path.join("2_recommendation_model", "saved_models", "roi_predictor.joblib")

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print(f">>> Model loaded successfully from {MODEL_PATH}")
else:
    print(f">>> Error: Model not found at {MODEL_PATH}. Please run train.py first.")
    model = None

# 3. 요청 데이터 구조 정의 (Pydantic)
class CampaignRequest(BaseModel):
    follower_count: int
    niche: str
    platform: str
    budget: int  # 예산은 ROI 계산 후 매출 추정에 사용

# 4. 헬스 체크 엔드포인트 (서버 상태 확인용)
@app.get("/")
def read_root():
    return {"status": "active", "service": "Nurihaus AI PoC"}

# 5. 추천 및 예측 엔드포인트 (핵심)
@app.post("/predict")
def predict_roi(request: CampaignRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Model is not loaded.")

    # 입력 데이터를 모델이 이해할 수 있는 DataFrame 형태로 변환
    input_data = pd.DataFrame([{
        'follower_count': request.follower_count,
        'niche': request.niche,
        'platform': request.platform
    }])

    try:
        # AI 예측 실행 (예상 ROI)
        predicted_roi = model.predict(input_data)[0]
        
        # 비즈니스 로직: 예상 매출 계산 (ROI * 예산)
        # ROI가 5.0이면 예산의 5배 효율이라는 뜻
        estimated_revenue = request.budget * predicted_roi

        return {
            "input_info": {
                "niche": request.niche,
                "platform": request.platform
            },
            "ai_analysis": {
                "predicted_roi": round(predicted_roi, 2),
                "estimated_revenue": round(estimated_revenue, 0),
                "confidence_score": "Low (Synthetic Data)" # 데모용 문구
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction Error: {str(e)}")

# 실행 방법 (터미널): uvicorn 3_backend_api_fastapi.main:app --reload