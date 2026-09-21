import requests
import html
import re
import html2text

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8830301039:AAGfaD0-tWU7WAqkuRPsXYZ7YrplcDuj4Io"
TELEGRAM_CHAT_ID = "8321315388"

def format_for_telegram_html(text):
    """Converts markdown to Telegram-safe HTML and wraps tables in <pre> tags."""
    # 1. Escape HTML entities (<, >, &) so Telegram doesn't mistake math operators for tags
    text = html.escape(text, quote=False)
    
    # 2. Convert Markdown links back to Telegram HTML links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    
    # 3. Convert inline backticks to <code> tags
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # 4. Find markdown tables and wrap them in <pre> tags for perfect monospaced alignment
    lines = text.split('\n')
    out = []
    table_buffer = []
    
    for line in lines:
        if '|' in line:
            table_buffer.append(line)
        else:
            if table_buffer:
                # If the block contains the markdown header separator, wrap it
                if any('---' in t for t in table_buffer):
                    out.append('<pre>')
                    out.extend(table_buffer)
                    out.append('</pre>')
                else:
                    out.extend(table_buffer)
                table_buffer = []
            out.append(line)
            
    if table_buffer:
        if any('---' in t for t in table_buffer):
            out.append('<pre>')
            out.extend(table_buffer)
            out.append('</pre>')
        else:
            out.extend(table_buffer)
            
    return '\n'.join(out)

def fetch_daily_problem():
    url = "https://leetcode.com/graphql"
    query = """
    query {
      activeDailyCodingChallengeQuestion {
        date
        link
        question {
          title
          difficulty
          content
        }
      }
    }
    """
    
    response = requests.post(
        url, 
        json={"query": query}, 
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    
    data = response.json()["data"]["activeDailyCodingChallengeQuestion"]
    q_data = data["question"]
    
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = False 
    text_maker.bypass_tables = False
    text_maker.ignore_emphasis = True  # Strip ** and _ to prevent Telegram rendering crashes
    text_maker.body_width = 0 
    
    raw_html = q_data["content"]
    raw_markdown = text_maker.handle(raw_html).strip()
    
    # Truncate BEFORE HTML formatting so we don't accidentally chop a tag in half
    if len(raw_markdown) > 3500:
        raw_markdown = raw_markdown[:3500] + "\n\n...[Content truncated due to length. Read full on LeetCode]"
        
    clean_html = format_for_telegram_html(raw_markdown)
    
    return {
        "date": data["date"],
        "title": q_data["title"],
        "difficulty": q_data["difficulty"],
        "link": "https://leetcode.com" + data["link"],
        "content": clean_html
    }

def send_to_telegram(problem):
    message = (
        f"📅 <b>LeetCode Daily:</b> {problem['date']}\n"
        f"🔥 <b>{problem['title']}</b> ({problem['difficulty']})\n"
        f"🔗 <a href='{problem['link']}'>{problem['link']}</a>\n\n"
        f"📝 <b>Problem Statement:</b>\n{problem['content']}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": True,
        "parse_mode": "HTML"  # Enables rich formatting and <pre> tags
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send: {response.text}")

if __name__ == "__main__":
    daily_problem = fetch_daily_problem()
    send_to_telegram(daily_problem)