import os
from dotenv import load_dotenv
import requests
import datetime

load_dotenv()  # Load environment variables from .env file
# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LEETCODE_USERNAME = os.getenv("LEETCODE_USERNAME")

if not all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, LEETCODE_USERNAME]):
    raise ValueError("Missing environment variables.")

# Fetch recent accepted submissions using LeetCode's internal GraphQL API
url = "https://leetcode.com/graphql"
query = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    title
    timestamp
  }
}
"""

response = requests.post(url, json={
    "query": query, 
    "variables": {"username": LEETCODE_USERNAME, "limit": 15}
}).json()

submissions = response.get("data", {}).get("recentAcSubmissionList", [])

# Calculate current date in IST (UTC + 5:30) using modern timezone-aware methods
tz_offset = datetime.timedelta(hours=5, minutes=30)
ist_now = datetime.datetime.now(datetime.timezone.utc) + tz_offset
today_str = ist_now.strftime("%Y-%m-%d")

# Check if any accepted submission matches today's date
solved_today = False
solved_title = ""
for sub in submissions:
    # Use modern timezone-aware timestamp conversion
    sub_time = datetime.datetime.fromtimestamp(int(sub["timestamp"]), datetime.timezone.utc) + tz_offset
    if sub_time.strftime("%Y-%m-%d") == today_str:
        solved_today = True
        solved_title = sub["title"]
        break

# Determine the message based on whether a problem was solved
if not solved_today:
    msg = (
        "🚨 Accountability Alert! 🚨\n\n"
        f"Hey {LEETCODE_USERNAME}, you haven't solved a LeetCode problem today. "
        "Get to work before the day ends!"
    )
else:
    msg = (
        "✅ Daily Goal Reached! ✅\n\n"
        f"Great work, {LEETCODE_USERNAME}. You solved '{solved_title}' today. "
        "Keep up the momentum!"
    )

# Send the Telegram message
tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
requests.post(tg_url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
print("Telegram message sent successfully.")