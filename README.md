# 💄 AI Creator Matching Engine (Prototype): Creator-Campaign Matching Engine

**"Data-Driven Influencer Marketing Solution"**

## 📌 Project Overview
크리에이터 매칭 프로세스를 자동화하고, 캠페인 ROI를 예측하기 위해 개발된 AI 솔루션 PoC입니다.
![Live Demo Dashboard](./Live_Demo_image.png)
* **Tech Stack:** Python, FastAPI, Streamlit, PostgreSQL, Scikit-learn, Render

## 🗂️ Data Pipeline Strategy
본 프로젝트는 **정성적 기획**과 **대규모 정량 데이터**를 결합하여 모델의 신뢰성을 확보했습니다.

### 1. Feature Definition (Qualitative Analysis)
![Feature Definition](./Feature_Definition_image.jpg)
> **"What data actually matters?"**
* **목적:** 모델링에 필요한 핵심 변수(Feature)를 식별하기 위한 선행 연구
* **과정:** Instagram/YouTube의 실제 크리에이터 콘텐츠와 댓글 반응을 직접 수집 및 분석하여, 단순 팔로워 수가 아닌 '참여도(Engagement)'와 '콘텐츠 톤앤매너'를 주요 학습 Feature로 정의했습니다.

### 2. Base Model Training (Academic Dataset)
* **데이터 규모:** **150,000+** Influencer Profile Data
* **출처:** 학술 연구 목적으로 제공받은 대규모 인플루언서 데이터셋
* **역할:** 다양한 카테고리의 크리에이터 패턴을 학습하여 베이스 모델(Base Model)을 구축했습니다.

### 3. Fine-Tuning (Real-World Performance)
![Fine Tuning Dataset](./Fine_Tuning_Dataset.png)
> **"Optimization with Real Campaign Data"**
* **데이터 규모:** **25,000+** Past Campaign Logs
* **내용:** 실제 집행된 마케팅 캠페인의 성과 데이터(SQL DB)를 활용
* **역할:** 베이스 모델에 실제 성과(ROI, 도달률) 데이터를 파인튜닝(Fine-Tuning)하여 예측 정확도를 비즈니스 수준으로 최적화했습니다.
  
## 🚀 Key Features
1.  **AI-Based ROI Prediction:** 과거 스폰서십 데이터를 학습한 Random Forest 모델이 예상 ROI를 계산합니다.
2.  **Real-time Dashboard:** 마케터가 직관적으로 사용할 수 있는 웹 대시보드 (Streamlit).
3.  **Scalable Architecture:** API-First 설계로 모바일 앱이나 웹 서비스에 즉시 연동 가능.

## 🛠 Architecture
* **Frontend:** Streamlit (Cloud Deployed)
* **Backend:** FastAPI (Render Deployed)
* **Database:** PostgreSQL (Cloud Hosted)
* **AI Model:** Random Forest Regressor (v1.0)

## 👨‍💻 Developer
**Yongrak Park**
* AI Product Builder of Beauty Inside Lab Inc.
* Kyonggi Univ. Economics & Startup Convergence
