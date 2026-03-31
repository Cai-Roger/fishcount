import streamlit as st
import pandas as pd

# 1. 基本設定
st.set_page_config(page_title="漁獲交易管理系統", layout="wide")

# --- 定義外觀樣式函數 ---
def apply_gray_style(df, cols):
    valid_cols = [c for c in cols if c in df.columns]
    def _style(val):
        return "background-color: #f0f2f6; color: #888888;"
    try:
        return df.style.map(_style, subset=valid_cols)
    except AttributeError:
        return df.style.applymap(_style, subset=valid_cols)

# --- 2. 初始化 Session State ---

if 'fish_master' not in st.session_state:
    st.session_state.fish_master = pd.DataFrame({
        "魚種": ["曲腰魚", "鰱魚", "吳郭魚", "鯽魚", "鯉魚", "青魚", "鯁魚", "泥鰍", "草魚", "溪蝦", "溪哥仔魚", "台灣石賓魚"],
        "單價": [385, 90, 95, 90, 75, 110, 70, 185, 110, 245, 240, 285]
    })

if 'all_receipts' not in st.session_state:
    st.session_state.all_receipts = []

if 'editor_key' not in st.session_state:
    st.session_state.editor_key = 0

# --- 3. 側邊欄導覽 ---
st.sidebar.title("⚙️ 系統目錄")
page = st.sidebar.radio("✨", ["💻主程式", "🛠️ 品項名稱及價格設定"])

# ==========================================
# 頁面：品項管理設定
# ==========================================
if page == "🛠️ 品項名稱及價格設定":
    st.title("🛠️ 品項與價格管理")
    st.write("您可以在此修改現有魚種、調整價格，或是新增/刪除品項。")
    
    new_master = st.data_editor(
        st.session_state.fish_master,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        height=600,
        column_config={
            "單價": st.column_config.NumberColumn("預設單價", format="%d 元", min_value=0)
        },
        key="master_editor"
    )
    
    if st.button("💾 儲存並套用修改"):
        st.session_state.fish_master = new_master
        st.success("設定已更新！")

# ==========================================
# 頁面：魚獲計算機 (主程式)
# ==========================================
else:
    st.title("🐟 漁獲交易彙整系統")

    # --- 總價目標區間設定 ---
    st.subheader("🎯 第一步：設定本次交易目標區間")
    with st.expander("點擊設定預算範圍", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            target_min = st.number_input("最低目標總價 (元)", min_value=0, value=85770, step=1000)
        with c2:
            target_max = st.number_input("最高目標總價 (元)", min_value=0, value=88500, step=1000)
    
    # 即時計算已紀錄單據的總額
    recorded_total_so_far = sum(r["小計"].sum() for r in st.session_state.all_receipts)
    remaining_budget = target_max - recorded_total_so_far

    st.info(f"📊 目前狀態：已紀錄金額 **{recorded_total_so_far:,.0f}** 元 / 最高目標 **{target_max:,.0f}** 元 (剩餘額度: **{remaining_budget:,.0f}** 元)")

    st.divider()

    df_init = st.session_state.fish_master.copy()
    df_init["數量/斤"] = 0

    st.subheader("⚖️ 第二步：輸入當前魚獲數量")

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
        height=600,
        key=f"editor_{st.session_state.editor_key}" 
    )

    edited_df["小計"] = edited_df["單價"] * edited_df["數量/斤"]
    current_total = edited_df["小計"].sum()

    st.write(f"**當前這筆金額： {current_total:,.0f} 元**")

    # 按鈕區
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("📝 記錄此單據 (存至下方)", use_container_width=True, type="primary"):
            if len(st.session_state.all_receipts) >= 3:
                st.error("❌ 已達三張單據上限！")
            elif current_total == 0:
                st.warning("⚠️ 請先輸入數量再記錄。")
            elif (recorded_total_so_far + current_total) > target_max:
                st.error(f"⚠️ 超出目標範圍！加上此單總額將達 {recorded_total_so_far + current_total:,.0f} 元，已超過上限 {target_max:,.0f} 元。")
            else:
                valid_record = edited_df[edited_df["數量/斤"] > 0].copy()
                st.session_state.all_receipts.append(valid_record)
                st.success(f"✅ 已記錄單據")
                st.rerun()

    with col_btn2:
        if st.button("🧹 清空上方輸入", use_container_width=True):
            st.session_state.editor_key += 1 
            st.rerun()

    with col_btn3:
        if st.button("🔄 全部重設 (清空所有)", use_container_width=True):
            st.session_state.all_receipts = []
            st.session_state.editor_key += 1
            st.rerun()

    st.divider()

    # --- 下方：顯示已紀錄單據 (新增單個刪除功能) ---
    st.subheader("📋 已紀錄單據明細")
    if not st.session_state.all_receipts:
        st.info("尚無紀錄單據。")
    else:
        # 根據單據數量動態產生欄位
        cols = st.columns(len(st.session_state.all_receipts))
        for i, r_df in enumerate(st.session_state.all_receipts):
            with cols[i]:
                st.markdown(f"**📄 單據 #{i+1}**")
                display_df = r_df[["魚種", "單價", "數量/斤", "小計"]]
                styled_display = apply_gray_style(display_df, ["魚種", "單價", "小計"])
                st.dataframe(styled_display, hide_index=True, use_container_width=True)
                
                receipt_sum = r_df['小計'].sum()
                st.markdown(f"**單總計：<span style='color:#e74c3c;'>{receipt_sum:,.0f} 元</span>**", unsafe_allow_html=True)
                
                # 👈 新增：刪除單張單據按鈕
                if st.button(f"🗑️ 刪除單據 #{i+1}", key=f"delete_btn_{i}", use_container_width=True):
                    st.session_state.all_receipts.pop(i) # 移除清單中第 i 個元素
                    st.rerun() # 重新整理頁面

    st.divider()

    # 最下方：總結報表
    if st.session_state.all_receipts:
        st.subheader("📊 最終彙整報表 (總結)")
        combined_df = pd.concat(st.session_state.all_receipts)
        
        # 彙整相同魚種
        summary_df = combined_df.groupby(["魚種", "單價"], as_index=False)[["數量/斤", "小計"]].sum()
        summary_df = summary_df[["魚種", "單價", "數量/斤", "小計"]]
        
        styled_summary = apply_gray_style(summary_df, ["魚種", "單價", "小計"])
        st.dataframe(styled_summary, hide_index=True, use_container_width=True)
        
        final_qty = summary_df["數量/斤"].sum()
        final_price = summary_df["小計"].sum()
        
        c1, c2 = st.columns(2)
        with c1: 
            st.metric("📦 總計總數量", f"{final_qty} 斤")
        with c2: 
            if final_price < target_min:
                st.metric("💰 總計總金額", f"${final_price:,.0f} 元", delta="低於最低目標", delta_color="inverse")
            elif final_price > target_max:
                st.metric("💰 總計總金額", f"${final_price:,.0f} 元", delta="超出上限", delta_color="normal")
            else:
                st.metric("💰 總計總金額", f"${final_price:,.0f} 元", delta="符合目標區間")
