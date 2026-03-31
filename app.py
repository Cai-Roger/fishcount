import streamlit as st
import pandas as pd

# 1. 基本設定
st.set_page_config(page_title="漁獲多單彙整系統", layout="wide")
st.title("🐟 漁獲交易彙整系統")

# --- 定義表格上色函數 (淡灰階) ---
def apply_gray_style(df, cols):
    """將指定的欄位設定為淡灰色背景與灰色字體，用以區分唯讀欄位"""
    valid_cols = [c for c in cols if c in df.columns]
    
    def _style(val):
        return "background-color: #f0f2f6; color: #888888;"
        
    # 兼容不同版本的 Pandas
    try:
        return df.style.map(_style, subset=valid_cols)
    except AttributeError:
        return df.style.applymap(_style, subset=valid_cols)

# --- 2. 初始化 Session State ---
fish_base = {
    "魚種": ["曲腰魚", "鰱魚", "吳郭魚", "鯽魚", "鯉魚", "青魚", "鯁魚", "泥鰍", "草魚", "溪蝦", "溪哥仔魚", "台灣石賓魚"],
    "單價": [385, 90, 95, 90, 75, 110, 70, 185, 110, 245, 240, 285],
    "數量/斤": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
}

df_init = pd.DataFrame(fish_base)

if 'all_receipts' not in st.session_state:
    st.session_state.all_receipts = []

if 'editor_key' not in st.session_state:
    st.session_state.editor_key = 0

# --- 3. 上方：數據輸入區 (秤重區) ---
st.subheader("⚖️ 第一步：輸入當前魚獲數量")

# 將唯讀欄位加上灰階樣式
styled_init_df = apply_gray_style(df_init, ["魚種", "單價"])

edited_df = st.data_editor(
    styled_init_df,
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
    if st.button("📝 記錄此單據 (存至下方)", use_container_width=True, type="primary"):
        if len(st.session_state.all_receipts) >= 3:
            st.error("❌ 已達三張單據上限！請先清空所有紀錄。")
        elif current_total == 0:
            st.warning("⚠️ 請先輸入數量再記錄。")
        else:
            valid_record = edited_df[edited_df["數量/斤"] > 0].copy()
            st.session_state.all_receipts.append(valid_record)
            st.success(f"✅ 已成功記錄第 {len(st.session_state.all_receipts)} 張單據")
            st.rerun()

with col_btn2:
    if st.button("🧹 清空上方輸入 (填寫下一筆)", use_container_width=True):
        st.session_state.editor_key += 1 
        st.rerun()

with col_btn3:
    if st.button("🔄 全部重設 (刪除所有紀錄)", use_container_width=True):
        st.session_state.all_receipts = []
        st.session_state.editor_key += 1
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
            # 整理欄位順序並套用灰階 (明細表裡的魚種、單價、小計皆為顯示用)
            display_df = r_df[["魚種", "單價", "數量/斤", "小計"]]
            styled_display = apply_gray_style(display_df, ["魚種", "單價", "小計"])
            
            st.dataframe(styled_display, hide_index=True, use_container_width=True)
            st.markdown(f"**單總計：<span style='color:#e74c3c;'>{r_df['小計'].sum():,.0f} 元</span>**", unsafe_allow_html=True)

st.divider()

# --- 6. 最下方：最後總結報表 ---
if st.session_state.all_receipts:
    st.subheader("📊 最終彙整報表 (三張單總結)")
    
    combined_df = pd.concat(st.session_state.all_receipts)
    summary_df = combined_df.groupby(["魚種", "單價"], as_index=False)[["數量/斤", "小計"]].sum()
    summary_df = summary_df[["魚種", "單價", "數量/斤", "小計"]]
    
    # 總表套用灰階
    styled_summary = apply_gray_style(summary_df, ["魚種", "單價", "小計"])
    st.dataframe(styled_summary, hide_index=True, use_container_width=True)
    
    final_qty = summary_df["數量/斤"].sum()
    final_price = summary_df["小計"].sum()
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("📦 總計總數量", f"{final_qty} 斤")
    with c2:
        st.metric("💰 總計總金額 (TWD)", f"${final_price:,.0f} 元")
