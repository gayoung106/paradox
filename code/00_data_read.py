import pandas as pd

# SAV 파일 읽기
df = pd.read_spss("../raw/raw_data.sav")

# 데이터 크기 확인
print("데이터 크기:", df.shape)

# 상위 5개 행 확인
print(df.head())

# 전체 변수명 출력
print(df.columns.tolist())