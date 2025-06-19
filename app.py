import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from openai_api import get_schedule_from_chatgpt

# OpenAI API 初期化
load_dotenv()
client = OpenAI()

TASK_FILE = "task_db.json"

# タスク読み書き関数
def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

# UI画面分割
st.set_page_config(page_title="予定マネージャ", layout="wide")
page = st.sidebar.radio("📌 メニュー", ["📋 タスク管理", "📆 スケジュール表", "💬 ChatGPTに相談"])

# タスク管理
if page == "📋 タスク管理":
    st.title("📋 タスク管理")
    tasks = load_tasks()

    with st.form("add_task"):
        st.subheader("➕ 新しいタスクを追加")
        category = st.selectbox("カテゴリ", ["研究", "授業", "ゲーム制作", "その他"])
        task_name = st.text_input("タスク内容")
        priority = st.selectbox("優先度", ["高", "中", "低"])
        submitted = st.form_submit_button("追加")
        if submitted and task_name:
            tasks.append({
                "category": category,
                "name": task_name,
                "priority": priority,
                "done": False,
                "created": str(datetime.now())
            })
            save_tasks(tasks)
            st.success("✅ タスクを追加しました")
            st.rerun()

    st.subheader("📝 未完了タスク一覧")
    if not any(not t["done"] for t in tasks):
        st.info("未完了タスクはありません")
    else:
        for idx, task in enumerate(tasks):
            if not task["done"]:
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"📌 {task['name']}（{task['category']}・{task['priority']}）")
                with col2:
                    if st.button("完了", key=f"done_{idx}"):
                        tasks[idx]["done"] = True
                        save_tasks(tasks)
                        st.rerun()

# スケジュール生成
elif page == "📆 スケジュール表":
    st.title("📆 ChatGPTでスケジュール作成")
    tasks = load_tasks()
    available_hours = st.slider("作業可能時間（時間単位）", 1, 12, 6)

    if st.button("🧠 スケジュール生成！"):
        task_descriptions = "\n".join([
            f"- {t['name']}（{t['category']}・{t['priority']}）"
            for t in tasks if not t["done"]
        ])
        if not task_descriptions:
            st.warning("⚠️ 未完了タスクがありません")
        else:
            with st.spinner("ChatGPTが考え中..."):
                schedule = get_schedule_from_chatgpt(task_descriptions, available_hours)
            st.success("🗓️ 今日のスケジュール案")
            st.text_area("▼ ChatGPTの提案", schedule, height=300)

# ChatGPTに相談
elif page == "💬 ChatGPTに相談":
    st.title("💬 ChatGPTと予定の相談")
    st.write("例：")
    st.code("今夜は自由時間があります。おすすめの過ごし方は？")
    question = st.text_area("あなたの相談内容")
    if st.button("ChatGPTに聞いてみる") and question.strip():
        with st.spinner("ChatGPTが考え中..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": question}],
                temperature=0.7
            )
        st.success("🧠 ChatGPTの回答")
        st.markdown(response.choices[0].message.content)
