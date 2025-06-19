import streamlit as st
import json
import os
from datetime import datetime
from openai_api import get_schedule_from_chatgpt
from dotenv import load_dotenv

load_dotenv()

# JSONファイルパス
TASK_FILE = "task_db.json"

# タスクの読み込み
def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# タスクの保存
def save_tasks(tasks):
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

# タスク管理画面
st.title("🗂️ タスク管理 + 🧠 ChatGPTスケジュール生成")

# タスク一覧の読み込み
tasks = load_tasks()

# タスクの追加フォーム
with st.form("add_task"):
    st.subheader("➕ タスクを追加")
    category = st.selectbox("カテゴリ", ["研究", "授業", "ゲーム制作", "その他"])
    task_name = st.text_input("タスク名を入力")
    priority = st.selectbox("優先度", ["高", "中", "低"])
    submitted = st.form_submit_button("追加する")
    if submitted and task_name:
        tasks.append({
            "category": category,
            "name": task_name,
            "priority": priority,
            "done": False,
            "created": str(datetime.now())
        })
        save_tasks(tasks)
        st.success("✅ タスクを追加しました！")
        st.experimental_rerun()

# 未完了タスク一覧表示
st.subheader("📋 未完了タスク")
if not any(not t["done"] for t in tasks):
    st.info("未完了タスクはありません。")
else:
    for idx, task in enumerate(tasks):
        if not task["done"]:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(f"📌 **{task['name']}**（{task['category']}・{task['priority']}）")
            with col2:
                if st.button("完了", key=f"done_{idx}"):
                    tasks[idx]["done"] = True
                    save_tasks(tasks)
                    st.experimental_rerun()

# スケジュール生成
st.subheader("📆 ChatGPTで今日の予定を作る")
available_hours = st.slider("作業可能な時間（時間単位）", 1, 12, 6)

if st.button("🧠 スケジュール生成！"):
    # 未完了タスクをChatGPTに渡す
    task_descriptions = "\n".join([
        f"- {t['name']}（{t['category']}・{t['priority']}）"
        for t in tasks if not t["done"]
    ])
    if not task_descriptions:
        st.warning("未完了タスクがありません。")
    else:
        with st.spinner("ChatGPTが考えています..."):
            schedule = get_schedule_from_chatgpt(task_descriptions, available_hours)
        st.success("🧾 今日のスケジュールが完成しました！")
        st.text_area("提案されたスケジュール", schedule, height=300)
