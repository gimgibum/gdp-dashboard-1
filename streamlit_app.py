import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="세계 미세먼지 대시보드", layout="wide")

st.title("🌍 세계 미세먼지(PM2.5) 대시보드")
st.markdown("### OpenAQ 사용자 CSV 기반 시각화")

# -----------------------------
# CSV 파일 불러오기
# -----------------------------
csv_file = "openaq (1).csv"   # 파일명 고정 (괄호 없는 버전)

if not os.path.exists(csv_file):
    st.error(f"CSV 파일이 없습니다: {csv_file}")
    st.stop()

try:
    df = pd.read_csv(csv_file)
except Exception as e:
    st.error(f"CSV 불러오기 실패: {e}")
    st.stop()

# -----------------------------
# 데이터 확인
# -----------------------------
st.subheader("📄 데이터 미리보기")
st.write(df.head())

# 컬럼 이름 확인
st.write("컬럼 목록:", list(df.columns))

# -----------------------------
# PM2.5 데이터만 필터링
# -----------------------------
if "parameter" in df.columns:
    df_pm25 = df[df["parameter"].str.lower() == "pm25"]
else:
    st.error("CSV에 'parameter' 컬럼이 없습니다. PM2.5 데이터 필터링 불가.")
    st.stop()

if df_pm25.empty:
    st.error("PM2.5 데이터가 없습니다. CSV 내용을 확인하세요.")
    st.stop()

# -----------------------------
# 시간 변환
# -----------------------------
time_col = None
for col in ["date.utc", "date.local", "timestamp", "time", "datetime"]:
    if col in df_pm25.columns:
        time_col = col
        break

if time_col is None:
    st.error("시간 컬럼을 찾을 수 없습니다. (예: date.utc, date.local 등)")
    st.stop()

df_pm25[time_col] = pd.to_datetime(df_pm25[time_col], errors="coerce")
df_pm25 = df_pm25.dropna(subset=[time_col])

# -----------------------------
# 국가별 평균 시계열 집계
# -----------------------------
if "country" not in df_pm25.columns:
    st.error("CSV에 'country' 컬럼이 없습니다. 국가별 집계 불가.")
    st.stop()

df_grouped = (
    df_pm25.groupby([pd.Grouper(key=time_col, freq="M"), "country"])["value"]
    .mean()
    .reset_index()
)

st.subheader("📈 세계 PM2.5 월평균 추세")
fig = px.line(
    df_grouped,
    x=time_col,
    y="value",
    color="country",
    title="국가별 PM2.5 월평균 농도",
    labels={"value": "PM2.5 (µg/m³)", time_col: "날짜"},
)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 다운로드 버튼
# -----------------------------
st.subheader("⬇️ 데이터 다운로드")
out_csv = df_grouped.to_csv(index=False).encode("utf-8")
st.download_button("집계 데이터 다운로드 (CSV)", data=out_csv, file_name="pm25_summary.csv", mime="text/csv")

# -----------------------------
# 참고 정보
# -----------------------------
st.markdown("---")
st.markdown("#### 출처·주의")
st.markdown("""
- 공식 데이터: [OpenAQ](https://openaq.org)
- 참고 문서: [OpenAQ Docs](https://docs.openaq.org/)
- 사용자 CSV: 앱 루트의 `openaq.csv` 파일 사용
""")

st.caption("개발자 노트: 이 앱은 Streamlit + GitHub Codespaces 환경에서 제작됨.")
st.write("CSV 파일 크기:", df.shape)
st.write("PM2.5 필터링 후:", df_pm25.shape)
st.write("Groupby 후:", df_grouped.shape)
