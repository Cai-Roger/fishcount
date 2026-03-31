import streamlit as st
import pandas as pd

# 設定網頁標題
st.set_page_config(page_title="漁獲交易計算系統", layout="centered")

st.title("🐟 漁獲交易計算系統")
st.write("請在下表輸入**數量/斤**，系統將自動計算金額。")

# 1. 根據你的 Excel 建立初始資料
# 這裡固定了魚種和單價，讓使用者只需專注於輸入數量
default_data = {
    "魚種": ["曲腰魚", "鰱魚", "吳郭魚", "鯽魚", "鯉魚", "青魚", "鯁魚", "泥鰍", "草魚", "溪蝦", "溪哥仔魚", "台灣石賓魚"],
    "單價": [385, 90, 95, 90, 75, 110, 70, 185, 110, 245, 240, 285],
    "數量/斤": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # 初始數量設為 0
}

df = pd.DataFrame(default_data)

# 2. 建立互動式編輯表格
st.subheader("🛒 交易清單編輯")

# 使用 st.data_editor 讓表格可編輯
# 我們鎖定「魚種」和「單價」不讓使用者修改，只開放「數量/斤」
edited_df = st.data_editor(
    df,
    column_config={
        "魚種": st.column_config.Column(disabled=True),
        "單價": st.column_config.NumberColumn("單價 (元)", disabled=True, format="%d"),
        "數量/斤": st.column_config.NumberColumn("數量/斤", min_value=0, step=1),
    },
    hide_index=True,
    use_container_width=True,
)

# 3. 計算邏輯 (核心功能)
# 計算每一列的小計
edited_df["小計"] = edited_df["單價"] * edited_df["數量/斤"]

# 計算總金額
total_amount = edited_df["小計"].sum()

st.divider()

# 4. 顯示結果
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 計算結果明細")
    # 只顯示有數量的品項（小計大於 0 的）
    result_display = edited_df[edited_df["小計"] > 0]
    if not result_display.empty:
        st.dataframe(result_display[["魚種", "數量/斤", "小計"]], hide_index=True)
    else:
        st.info("目前尚未輸入任何數量。")

with col2:
    st.subheader("💰 總計金額")
    # 用醒目的方式顯示總金額
    st.metric(label="應收總額 (TWD)", value=f"${total_amount:,.0f}")
    
    if total_amount > 0:
        if st.button("確認成交並清除資料"):
            st.success("交易已記錄！(此處可串接資料庫存檔)")
            # 這裡可以加入存入 CSV 或資料庫的程式碼
