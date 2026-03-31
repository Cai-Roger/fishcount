import streamlit as st
import pandas as pd

# 1. 基本設定
st.set_page_config(page_title="漁獲多單彙整系統", layout="wide")
st.title("🐟 漁獲交易彙整系統 (最多三張單)")

# --- 2. 初始化 Session State ---
# 預設魚種資料
fish_base = {
    "魚種": ["曲腰魚", "鰱魚", "吳郭魚", "鯽魚", "鯉魚", "青魚", "鯁魚", "泥鰍", "草魚", "溪蝦", "溪哥仔魚", "台灣石賓魚"],
    "單價": [385, 90, 95, 90, 75, 110, 70, 185, 110, 245, 240, 285]
}

# 儲存已記錄的單據
if 'all_receipts' not in st.session_state:
    st.session_state.all_receipts = []

# 用於控制上方輸入表格的重置
if 'input_df' not in st.session_state:
    df_init = pd.DataFrame(fish_base)
    df_init["數量/斤"] = 0
    st.session_state.input_df = df_init

# --- 3. 上方：數據輸入區 (秤重區) ---
st.subheader("⚖️ 第一步：輸入當前魚獲數量")

# 這裡使用一個表單或 key 來確保可以被重置
edited_df = st.data_editor(
    st.session_state.input_df,
    column_config={
        "魚種": st.column_config.Column(disabled=True),
        "單價": st.column_config.NumberColumn("單價 (元)", disabled=True, format="%d"),
        "數量/斤": st.column_config.NumberColumn("數量/斤", min_value=0, step=1),
    },
    hide_index=True,
    use_container_width=True,
    key="editor"
)

# 計算目前編輯中的小計
temp_df = edited_df.copy()
temp_df["小計"] = temp_df["單價"] * temp_df["數量/斤"]
current_total = temp_df["小計"].sum()

# --- 4. 中間：操作按鈕 ---
col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    # 紀錄單據按鈕
    if st.button("📝 記錄此單據 (存至下方)", use_container_width=True, type="primary"):
        if len(st.session_state.all_receipts) >= 3:
            st.error("❌ 已達三張單據上限！")
        elif current_total == 0:
            st.warning("⚠️ 請先輸入數量。")
        else:
            # 只存有數量的資料
            valid_record = temp_df[temp_df["數量/斤"] > 0].copy()
            st.session_state.all_receipts.append(valid_record)
            st.success(f"✅ 已成功記錄第 {len(st.session_state.all_receipts)} 張單據")
            st.rerun()

with col_btn2:
    # 清空上方輸入按鈕
    if st.button("🧹 清空上方輸入 (填寫下一筆)", use_container_width=True):
        # 重新初始化 input_df
        df_reset = pd.DataFrame(fish_base)
        df_reset["數量/斤"] = 0
        st.session_state.input_df = df_reset
        # 由於 Streamlit 的 data_editor key 機制，需要 rerun 來刷新畫面
        st.rerun()

with col_btn3:
    # 全部重設
    if st.button("🔄 全部重設 (刪除所有紀錄)", use_container_width=True):
        st.session_state.all_receipts = []
        df_reset = pd.DataFrame(fish_base)
        df_reset["數量/斤"] = 0
        st.session_state.input_df = df_reset
        st.rerun()

st.divider()

# --- 5. 下方：單據顯示區 ---
st.subheader("📋 已紀錄單據明細")
if not st.session_state.all_receipts:
    st.info("尚無紀錄單據。")
else:
    cols = st.columns(len(st.session_state.all_receipts))
    for i, r_df in enumerate(st.session_state.all_receipts):
        with cols[i]:
            st.markdown(f"**📄 單據 #{i+1}**")
            st.dataframe(r_df[["魚種", "數量/斤", "小計"]], hide_index=True, use_container_width=True)
            st.write(f"單總計：{r_df['小計'].sum():,.0f} 元")

st.divider()

# --- 6. 最下方：最後總結報表 ---
if st.session_state.all_receipts:
    st.subheader("📊 三張單據 - 最終彙整報表")
    
    # 合併所有單據
    combined_df = pd.concat(st.session_state.all_receipts)
    
    # 按照魚種和單價進行群組加總 (彙整三張單中相同的魚)
    summary_df = combined_df.groupby(["魚種", "單價"], as_index=False)[["數量/斤", "小計"]].sum()
    
    # 顯示總表
    st.table(summary_df)
    
    # 計算全場總計
    final_qty = summary_df["數量/斤"].sum()
    final_price = summary_df["小計"].sum()
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("總計總數量 (斤)", f"{final_qty} 斤")
    with c2:
        st.metric("總計總金額 (TWD)", f"${final_price:,.0f} 元")
