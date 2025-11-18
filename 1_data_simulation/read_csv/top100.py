import pandas as pd

# 원본 CSV 파일 이름
input_filename = '1_data_simulation\influencer_marketing_roi_dataset.csv'
# 저장할 새 CSV 파일 이름
output_filename = 'influencer_marketing_roi_dataset_top100_rows.csv'

try:
    # CSV 파일에서 처음 100개 행만 읽어오기
    # nrows=100 : 처음 100개의 행(row)을 읽습니다.
    df_top100 = pd.read_csv(input_filename, nrows=100)
    
    # 새 CSV 파일로 저장하기 (인덱스 제외)
    df_top100.to_csv(output_filename, index=False)
    
    print(f"'{input_filename}' 파일의 처음 100개 행을 '{output_filename}' 파일로 성공적으로 저장했습니다.")
    print(f"저장된 데이터의 크기 (행, 열): {df_top100.shape}")

except FileNotFoundError:
    print(f"오류: '{input_filename}' 파일을 찾을 수 없습니다. 파일을 업로드했는지 확인해주세요.")
except Exception as e:
    print(f"파일 처리 중 오류가 발생했습니다: {e}")