from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def get_schedule_from_chatgpt(task_list, available_hours):
    prompt = f"""以下のタスクリストを、今日のスケジュールとして時間帯に割り振ってください。
作業可能時間: {available_hours} 時間
タスク一覧:
{task_list}

出力形式（例）:
[09:00〜10:00] 英語レポート（授業）
[10:00〜11:00] 敵モンスター登録（ゲーム制作）
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content
