import streamlit as st
import pandas as pd
import numpy as np

# 設定網頁標題與寬度
st.set_page_config(page_title="我的 Streamlit 軟體", page_icon="🚀", layout="centered")

st.title("🚀 我的 Streamlit 應用程式")
st.write("Streamlit 讓 Web 開發變得超級簡單，特別適合做工具或儀表板！")

# ----------------------------------------
# 功能一：狀態管理 (Session State) 範例 - 待辦清單
# ----------------------------------------
st.header("📝 簡易待辦清單")

# 初始化 session_state (為了讓每次網頁重新整理時，資料不會消失)
if 'todos' not in st.session_state:
    st.session_state.todos = []

# 排版：使用欄位 (Columns) 將輸入框和按鈕並排
col1, col2 = st.columns([4, 1])

with col1:
    # 這裡的文字輸入框
    new_task = st.text_input("輸入新任務...", label_visibility="collapsed", placeholder="今天想做什麼？")

with col2:
    if st.button("新增", use_container_width=True):
        if new_task:
            st.session_state.todos.append(new_task)
            st.rerun() # 強制重新整理頁面

# 顯示任務
if st.session_state.todos:
    for i, task in enumerate(st.session_state.todos):
        # 產生核取方塊
        done = st.checkbox(task, key=f"task_{i}")
        if done:
            st.write(f"~~{task}~~ (已完成!)")
else:
    st.info("目前沒有任務，趕快新增一個吧！")

st.divider() # 分隔線

# ----------------------------------------
# 功能二：數據視覺化 (Streamlit 的強項)
# ----------------------------------------
st.header("📊 數據圖表展示")
st.write("你可以輕鬆把 Pandas DataFrame 變成圖表：")

# 隨機生成 20 天的假數據
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['產品 A', '產品 B', '產品 C']
)

# 一行程式碼生成折線圖
st.line_chart(chart_data)
