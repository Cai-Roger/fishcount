import streamlit as st
import pandas as pd

# 1. 基本設定
st.set_page_config(page_title="漁獲多單彙整系統", layout="wide")
st.title("🐟 漁獲交易彙整系統")

# --- 2. 初始化 Session State ---
# 預設魚種與單價資料
fish_base = {
    "魚種": ["曲腰魚", "鰱魚", "吳郭魚", "鯽魚", "鯉魚", "青魚", "鯁魚", "泥鰍", "草魚", "溪蝦", "溪哥仔魚", "台灣石賓魚"],
    "單價": [385, 90, 95, 90, 75, 110, 70, 185, 110, 245, 240, 285],
    "數量/斤": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # 預設數量為 0
}

df_init = pd.DataFrame(fish_base)

# 儲存已記錄的單據
if 'all_receipts' not in st.session_state:
    st.session_state.all_receipts = []

# 建立一個 Editor Key 控制器 (用來強制重置表格)
if 'editor_key' not in st.session_state:
    st.session_state.editor_key = 0

# --- 3. 上方：數據輸入區 (秤重區) ---
st.subheader("⚖️ 第一步：輸入當前魚獲數量")

# 注意這裡的 key 使用了 f-string，當 st.session_state.editor_key 改變時，表格就會強制重置為 df_init
edited_df = st.data_editor(
    df_init,
    column_config={
        "魚種": st.column_config.Column(disabled=True),
        "單價": st.column_config.NumberColumn("單價 (元)", disabled=True, format="%d"),
        "數量/斤": st.column_config.NumberColumn("數量/斤", min_value=0, step=1),
    },
    hide_index=True,
    use_container_width=True,
    key=f"editor_{st.session_state.editor_key}" 
)

# 計算目前編輯中的小計
edited_df["小計"] = edited_df["單價"] * edited_df["數量/斤"]
current_total = edited_df["小計"].sum()

st.write(f"**當前這筆預估總額： {current_total:,.0f} 元**")

# --- 4. 中間：操作按鈕 ---
col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    # 紀錄單據按鈕
    if st.button("📝 記錄此單據 (存至下方)", use_container_width=True, type="primary"):
        if len(st.session_state.all_receipts) >= 3:
            st.error("❌ 已達三張單據上限！請先清空所有紀錄。")
        elif current_total == 0:
            st.warning("⚠️ 請先輸入數量再記錄。")
        else:
            # 只存有數量的資料
            valid_record = edited_df[edited_df["數量/斤"] > 0].copy()
            st.session_state.all_receipts.append(valid_record)
            st.success(f"✅ 已成功記錄第 {len(st.session_state.all_receipts)} 張單據")
            st.rerun()

with col_btn2:
    # 真正能清空表格的按鈕
    if st.button("🧹 清空上方輸入 (填寫下一筆)", use_container_width=True):
        # 只要把 key + 1，Streamlit 就會忘記剛才輸入的數字，重新載入 0
        st.session_state.editor_key += 1 
        st.rerun()

with col_btn3:
    # 全部重設
    if st.button("🔄 全部重設 (刪除所有紀錄)", use_container_width=True):
        st.session_state.all_receipts = []
        st.session_state.editor_key += 1 # 同時清空上方的輸入
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
            # 這裡把 "單價" 加進來顯示了
            st.dataframe(r_df[["魚種", "單價", "數量/斤", "小計"]], hide_index=True, use_container_width=True)
            st.markdown(f"**單總計：<span style='color:#e74c3c;'>{r_df['小計'].sum():,.0f} 元</span>**", unsafe_allow_html=True)

st.divider()

# --- 6. 最下方：最後總結報表 ---
if st.session_state.all_receipts:
    st.subheader("📊 最終彙整報表 (三張單總結)")
    
    # 合併所有單據
    combined_df = pd.concat(st.session_state.all_receipts)
    
    # 按照魚種和單價進行群組加總
    summary_df = combined_df.groupby(["魚種", "單價"], as_index=False)[["數量/斤", "小計"]].sum()
    
    # 確保顯示順序為：魚類、單價、斤數、總計(小計)
    summary_df = summary_df[["魚種", "單價", "數量/斤", "小計"]]
    
    # 顯示總表
    st.dataframe(summary_df, hide_index=True, use_container_width=True)
    
    # 計算全場總計
    final_qty = summary_df["數量/斤"].sum()
    final_price = summary_df["小計"].sum()
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("📦 總計總數量", f"{final_qty} 斤")
    with c2:
        st.metric("💰 總計總金額 (TWD)", f"${final_price:,.0f} 元")
