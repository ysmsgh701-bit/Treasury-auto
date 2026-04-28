import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class Notifier:
    def __init__(self):
        self.slack_url = os.getenv("SLACK_WEBHOOK_URL")

    def send_slack(self, message):
        if not self.slack_url or "your_slack_webhook" in self.slack_url:
            print(f"[Console Mock] Slack Message: {message}")
            return True
        
        payload = {"text": message}
        try:
            response = requests.post(
                self.slack_url, data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending slack message: {e}")
            return False

    def notify_dday(self, item_name, target_date, d_day, amount, bank):
        msg = f"🔔 *[{d_day}] 금융 일정 알림*\n"
        msg += f"• 항목: {item_name} ({bank})\n"
        msg += f"• 기일: {target_date}\n"
        msg += f"• 금액: {amount:,.0f}원\n"
        msg += f"• 상태: 현재 {d_day} 입니다. 확인 부탁드립니다."
        
        return self.send_slack(msg)
