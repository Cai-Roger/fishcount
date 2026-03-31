import streamlit as st
import pandas as pd

# 設定網頁標題
st.set_page_config(page_title="漁獲多單交易系統", layout="centered")

st.title("🐟 漁獲多單交易系統")

# --- 1. 初始化資料與 Session State ---
# 預設魚種與單價
fish_data = {
    "魚種": ["曲腰魚", "鰱魚", "吳郭魚", "鯽魚", "鯉魚", "青魚", "鯁魚", "泥鰍", "草魚", "溪蝦", "溪哥仔魚", "台灣石賓魚"],
    "單價": [385, 90, 95, 90, 75, 110, 70, 185, 110, 245, 240, 285]
}

# 用於儲存已完成的單據清單 (最多 3 張)
if 'receipts' not in st.session_state:
    st.session_state.receipts = []

# --- 2. 輸入區域 (秤重區) ---
st.subheader("⚖️ 當前秤重輸入")

# 建立初始輸入 DataFrame
input_df = pd.DataFrame(fish_data)
input_df["數量/斤"] = 0

# 使用 data_editor 進行輸入
edited_input = st.data_editor(
    input_df,
    column_config={
        "魚種": st.column_config.Column(disabled=True),
        "單價": st.column_config.NumberColumn("單價 (元)", disabled=True, format="%d"),
        "數量/斤": st.column_config.NumberColumn("數量/斤", min_value=0, step=1),
    },
    hide_index=True,
    use_container_width=True,
    key="weighting_table"
)

# 計算當前秤重區的小計
edited_input["小計"] = edited_input["單價"] * edited_input["數量/斤"]
current_total = edited_input["小計"].sum()

st.write(f"**當前預估總額： {current_total:,.0f} 元**")

# --- 3. 單據操作按鈕 ---
col_btn1, col_btn2 = st.columns([1, 1])

with col_btn1:
    if st.button("➕ 完成並記錄此單據", use_container_width=True):
        if len(st.session_state.receipts) >= 3:
            st.error("❌ 已達上限（3張單據），請先清空再記錄。")
        elif current_total == 0:
            st.warning("⚠️ 請先輸入數量再進行記錄。")
        else:
            # 只紀錄有數量的品項
            final_items = edited_input[edited_input["數量/斤"] > 0].copy()
            st.session_state.receipts.append(final_items)
            st.success(f"✅ 已存入第 {len(st.session_state.receipts)} 張單據")
            st.rerun()

with col_btn2:
    if st.button("🗑️ 清空所有單據", use_container_width=True):
        st.session_state.receipts = []
        st.rerun()

st.divider()

# --- 4. 顯示已記錄的單據 ---
st.subheader("📋 已紀錄單據明細")

if not st.session_state.receipts:
    st.info("尚無紀錄單據")
else:
    # 建立三個欄位來顯示三張單 (或者垂直排列)
    for idx, r_df in enumerate(st.session_state.receipts):
        with st.expander(f"📄 單據 #{idx + 1} - 詳情", expanded=True):
            st.table(r_df[["魚種", "單價", "數量/斤", "小計"]])
            st.write(f"**此單總計： {r_df['小計'].sum():,.0f} 元**")

# --- 5. 總計報表 (最下方) ---
if st.session_state.receipts:
    st.divider()
    st.subheader("📈 全單總結報表 (Total Summary)")
    
    # 合併所有單據資料進行計算
    all_data = pd.concat(st.session_state.receipts)
    grand_total_qty = all_data["數量/斤"].sum()
    grand_total_price = all_data["小計"].sum()
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("總累計數量 (斤)", f"{grand_total_qty} 斤")
    with c2:
        st.metric("總累計金額 (TWD)", f"${grand_total_price:,.0f}")
