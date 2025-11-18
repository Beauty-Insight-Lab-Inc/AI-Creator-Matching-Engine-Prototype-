import pandas as pd

# 원본 CSV 파일 이름 (업로드하신 파일 이름)
input_filename = '1_data_simulation\influencer_marketing_roi_dataset.csv'
# 'Beauty' 카테고리 데이터만 저장할 새 파일 이름
output_filename = 'beauty_influencers_dataset.csv'

try:
    # CSV 파일을 pandas DataFrame으로 읽어옵니다.
    print(f"'{input_filename}' 파일을 읽는 중...")
    df = pd.read_csv(input_filename)

    # 'influencer_category' 열의 값이 'Beauty'인 행들만 필터링합니다.
    # (참고: 데이터 샘플을 보니 'Fitness', 'Food' 등 대소문자를 구분하는 것 같아 'Beauty'로 지정했습니다.)
    print("'influencer_category'가 'Beauty'인 데이터 필터링 중...")
    beauty_df = df[df['influencer_category'] == 'Beauty']

    # 필터링된 데이터를 새 CSV 파일로 저장합니다.
    # index=False는 pandas가 추가하는 인덱스 열을 저장하지 않도록 합니다.
    beauty_df.to_csv(output_filename, index=False, encoding='utf-8')

    print(f"필터링 완료! '{output_filename}' 파일에 {len(beauty_df)}개의 행이 저장되었습니다.")

except FileNotFoundError:
    print(f"오류: '{input_filename}' 파일을 찾을 수 없습니다. 파일 이름과 경로를 확인하세요.")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")