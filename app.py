import streamlit as st
import requests
import pandas as pd
import time

# -----------------------------
# إعداد ثابت لطول كل شرط
condition_lengths = {
    "1.00 مرتين": 2,
    "<1.05 مرتين": 2,
    "<1.05 ثلاث مرات": 3,
    "<1.20 ثلاث مرات": 3,
    "<1.20 أربع مرات": 4,
    "<2.00 أحد عشر مرة": 11
}

# -----------------------------
# تحميل البيانات من Stake
def fetch_crash_data(limit=50000, batch_size=1000):
    all_data = []
    url = "https://api.stake.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    for i in range(0, limit, batch_size):
        query = """
        query CrashRounds {
          crashRounds(first: %d, orderBy: id, orderDirection: desc) {
            id
            multiplier
            createdAt
          }
        }
        """ % batch_size

        try:
            response = requests.post(url, json={"query": query}, headers=headers)
            response.raise_for_status()
            data_json = response.json()

            if "data" not in data_json or "crashRounds" not in data_json["data"]:
                st.warning("⚠️ الرد من الخادم لا يحتوي على crashRounds.")
                continue

            data = data_json["data"]["crashRounds"]
            if not data:
                break
            all_data.extend(data)
            time.sleep(0.2)

        except Exception as e:
            st.error(f"❌ فشل في تحميل البيانات: {str(e)}")
            break

    if not all_data:
        return pd.DataFrame()

    df = pd.DataFrame(all_data)

    required_cols = {"multiplier", "id"}
    if not required_cols.issubset(df.columns):
        st.error("❌ البيانات المحملة لا تحتوي على الأعمدة المطلوبة.")
        return pd.DataFrame()

    df["multiplier"] = df["multiplier"].astype(float)
    return df[::-1].reset_index(drop=True)

# -----------------------------
# تحليل الشروط
def check_conditions(df):
    values = df["multiplier"].tolist()
    results = {
        "1.00 مرتين": 0,
        "<1.05 مرتين": 0,
        "<1.05 ثلاث مرات": 0,
        "<1.20 ثلاث مرات": 0,
        "<1.20 أربع مرات": 0,
        "<2.00 أحد عشر مرة": 0
    }

    green = []
    red = []
    blue = []

    for i in range(len(values)):
        for key in results:
            length = condition_lengths[key]
            if i + length > len(values):
                continue

            seq = values[i:i+length]

            match = False
            if key == "1.00 مرتين" and all(x == 1.00 for x in seq):
                match = True
            elif key == "<1.05 مرتين" and all(x < 1.05 for x in seq):
                match = True
            elif key == "<1.05 ثلاث مرات" and all(x < 1.05 for x in seq):
                match = True
            elif key == "<1.20 ثلاث مرات" and all(x < 1.20 for x in seq):
                match = True
            elif key == "<1.20 أربع مرات" and all(x < 1.20 for x in seq):
                match = True
            elif key == "<2.00 أحد عشر مرة" and all(x < 2.00 for x in seq):
                match = True

            if match:
                results[key] += 1
                future = values[i+length:i+length+140]
                if 1.05 in future and all(x >= 1.05 for x in future):
                    blue.append((i, key))
                elif 1.05 in future:
                    green.append((i, key))
                else:
                    red.append((i, key))

    return results, green, red, blue

# -----------------------------
# عرض النتائج
def display_results(df, results, green, red, blue):
    st.title("📊 تحليل نتائج Crash على Stake")
    st.markdown("### ✅ عدد تحقق الشروط (بشكل عام):")
    for k, v in results.items():
        st.markdown(f"- {k}: <span style='color:white'>{v}</span>", unsafe_allow_html=True)

    if green:
        st.markdown("### 🟩 تحقق الشرط وظهر بعده 1.05:")
        for idx, cond in green:
            if idx + 12 <= len(df):
                st.markdown(f"<span style='color:green'>✅ {cond}</span> عند الجولة {idx}", unsafe_allow_html=True)

    if red:
        st.markdown("### 🟥 تحقق الشرط ولم يظهر 1.05 بعده:")
        for idx, cond in red:
            if idx + 12 <= len(df):
                st.markdown(f"<span style='color:red'>❌ {cond}</span> عند الجولة {idx}", unsafe_allow_html=True)

    if blue:
        st.markdown("### 🔵 تحقق الشرط وظهر بعده 1.05 دون أي خسارة خلال 140 لعبة:")
        for idx, cond in blue:
            if idx + 12 <= len(df):
                st.markdown(f"<span style='color:blue'>💠 {cond}</span> عند الجولة {idx}", unsafe_allow_html=True)

# -----------------------------
# التشغيل
def main():
    df = fetch_crash_data()
    if df.empty:
        st.error("🚫 لا توجد بيانات لتحليلها.")
        return

    results, green, red, blue = check_conditions(df)
    display_results(df, results, green, red, blue)

if __name__ == "__main__":
    main()
