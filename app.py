import streamlit as st
import pandas as pd

# 1. 基本設定
st.set_page_config(page_title="漁獲交易進階系統", layout="wide")

# --- 定義外觀樣式函數 ---
def apply_gray_style(df, cols):
    valid_cols = [c for c in cols if c in df.columns]
    def _style(val):
        return "background-color: #f0f2f6; color: #888888;"
    try:
        return df.style.map(_style, subset=valid_cols)
    except AttributeError:
        return df.style.applymap(_style, subset=valid_cols)

# --- 2. 初始化 Session State (核心資料儲存) ---

# A. 初始魚種大清單 (Master List)
if 'fish_master' not in st.session_state:
    st.session_state.fish_master = pd.DataFrame({
        "魚種": ["曲腰魚", "鰱魚", "吳郭魚", "鯽魚", "鯉魚", "青魚", "鯁魚", "泥鰍", "草魚", "溪蝦", "溪哥仔魚", "台灣石賓魚"],
        "單價": [385, 90, 95, 90, 75, 110, 70, 185, 110, 245, 240, 285]
    })

# B. 儲存已記錄的單據
if 'all_receipts' not in st.session_state:
    st.session_state.all_receipts = []

# C. 編輯器重置 Key
if 'editor_key' not in st.session_state:
    st.session_state.editor_key = 0

# --- 3. 側邊欄導覽 ---
st.sidebar.title("⚙️ 系統選單")
page = st.sidebar.radio("前往頁面：", ["🐟 魚獲計算機", "🛠️ 品項管理設定"])

# ==========================================
# 頁面：品項管理設定
# ==========================================
if page == "🛠️ 品項管理設定":
    st.title("🛠️ 品項與價格管理")
    st.write("您可以在此修改現有魚種、調整價格，或是新增/刪除品項。修改後將即時套用到計算機。")
    
    # 使用 data_editor 修改 Master List
    # num_rows="dynamic" 允許使用者新增或刪除列
    new_master = st.data_editor(
        st.session_state.fish_master,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "單價": st.column_config.NumberColumn("預設單價", format="%d 元", min_value=0)
        },
        key="master_editor"
    )
    
    if st.button("💾 儲存並套用修改"):
        st.session_state.fish_master = new_master
        st.success("設定已更新！現在可以切換到「魚獲計算機」開始作業。")

# ==========================================
# 頁面：魚獲計算機
# ==========================================
else:
    st.title("🐟 漁獲交易彙整系統")

    # 準備輸入用的 DataFrame (從 Master List 產生)
    df_init = st.session_state.fish_master.copy()
    df_init["數量/斤"] = 0

    st.subheader("⚖️ 第一步：輸入當前魚獲數量")

    # 套用灰階樣式
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

    # 按鈕區
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("📝 記錄此單據 (存至下方)", use_container_width=True, type="primary"):
            if len(st.session_state.all_receipts) >= 3:
                st.error("❌ 已達三張單據上限！")
            elif current_total == 0:
                st.warning("⚠️ 請先輸入數量。")
            else:
                valid_record = edited_df[edited_df["數量/斤"] > 0].copy()
                st.session_state.all_receipts.append(valid_record)
                st.success(f"✅ 已記錄第 {len(st.session_state.all_receipts)} 張單據")
                st.rerun()

    with col_btn2:
        if st.button("🧹 清空上方輸入", use_container_width=True):
            st.session_state.editor_key += 1 
            st.rerun()

    with col_btn3:
        if st.button("🔄 全部重設", use_container_width=True):
            st.session_state.all_receipts = []
            st.session_state.editor_key += 1
            st.rerun()

    st.divider()

    # 下方：顯示已紀錄單據
    st.subheader("📋 已紀錄單據明細")
    if not st.session_state.all_receipts:
        st.info("尚無紀錄單據。")
    else:
        cols = st.columns(len(st.session_state.all_receipts))
        for i, r_df in enumerate(st.session_state.all_receipts):
            with cols[i]:
                st.markdown(f"**📄 單據 #{i+1}**")
                display_df = r_df[["魚種", "單價", "數量/斤", "小計"]]
                styled_display = apply_gray_style(display_df, ["魚種", "單價", "小計"])
                st.dataframe(styled_display, hide_index=True, use_container_width=True)
                st.markdown(f"**單總計：<span style='color:#e74c3c;'>{r_df['小計'].sum():,.0f} 元</span>**", unsafe_allow_html=True)

    st.divider()

    # 最下方：總結報表
    if st.session_state.all_receipts:
        st.subheader("📊 最終彙整報表 (總結)")
        combined_df = pd.concat(st.session_state.all_receipts)
        summary_df = combined_df.groupby(["魚種", "單價"], as_index=False)[["數量/斤", "小計"]].sum()
        summary_df = summary_df[["魚種", "單價", "數量/斤", "小計"]]
        
        styled_summary = apply_gray_style(summary_df, ["魚種", "單價", "小計"])
        st.dataframe(styled_summary, hide_index=True, use_container_width=True)
        
        final_qty = summary_df["數量/斤"].sum()
        final_price = summary_df["小計"].sum()
        
        c1, c2 = st.columns(2)
        with c1: st.metric("📦 總計總數量", f"{final_qty} 斤")
        with c2: st.metric("💰 總計總金額", f"${final_price:,.0f} 元")
