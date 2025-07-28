import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import openai
import schedule
import time
import json
import os
import datetime

# === CONFIGURATION ===
MY_EMAIL = "manojsomarowthu123@gmail.com"
MY_APP_PASSWORD = "yptq ivvi ryxp jdei"
OPENAI_KEY = "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"
openai.api_key = OPENAI_KEY

LOG_FILE = "sent_jobs.json"

# === HELPER: Load/Save Sent Job URLs ===
def load_sent():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return set(json.load(f))
    return set()

def save_sent(sent_set):
    with open(LOG_FILE, "w") as f:
        json.dump(list(sent_set), f)

# === SCRAPERS ===
def fetch_yc_jobs():
    url = "https://www.ycombinator.com/jobs"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.select("a.styles_jobListItem__zF9U6")[:10]
    jobs = []
    for a in items:
        title = a.find("h3").text.strip()
        company = a.find("h4").text.strip()
        link = "https://www.ycombinator.com" + a["href"]
        if any(k in title.lower() for k in ["ui", "ux", "data"]) and "senior" not in title.lower():
            jobs.append({"title": title, "company": company, "link": link})
    return jobs

def fetch_wellfound_jobs():
    url = "https://angel.co/jobs"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select("div.job-listing-template")[:10]
    jobs = []
    for c in cards:
        title_el = c.select_one("h4:not(.hidden)")
        company_el = c.select_one("div[itemprop='hiringOrganization']")
        link_el = c.find("a", href=True)
        if not (title_el and company_el and link_el): continue
        title = title_el.text.strip()
        company = company_el.text.strip()
        link = "https://angel.co" + link_el["href"]
        if any(k in title.lower() for k in ["ui", "ux", "data"]) and "senior" not in title.lower():
            jobs.append({"title": title, "company": company, "link": link})
    return jobs

# === OPENAI LINKEDIN MESSAGE ===
def linkedin_message(job):
    prompt = (
        f"Write a short friendly LinkedIn message to a recruiter for {job['title']} "
        f"at {job['company']}. I’m an eager entry‑level candidate named Manoj."
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            max_tokens=100
        )
        return resp.choices[0].message.content.strip()
    except:
        return "Hi, I'm interested in this opportunity and would love to connect!"

# === FORMAT EMAIL ===
def format_email(jobs):
    html = f"<h2>📅 Job Alerts — {datetime.date.today()}</h2>"
    for j in jobs:
        msg = linkedin_message(j)
        html += f"""
        <h3>{j['title']} — {j['company']}</h3>
        🔗 <a href="{j['link']}">Apply Here</a><br>
        💬 LinkedIn message:<br>
        <blockquote>{msg}</blockquote><hr>
        """
    return html

# === SEND EMAIL ===
def send_email(html_body):
    msg = MIMEText(html_body, "html")
    msg["From"] = MY_EMAIL
    msg["To"] = MY_EMAIL
    msg["Subject"] = "🚀 UI/UX & Data Analyst Job Alerts"

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(MY_EMAIL, MY_APP_PASSWORD)
        s.send_message(msg)
    print("✅ Email sent")

# === MAIN WORKFLOW ===
def job_runner():
    print("🔍 Fetching jobs...")
    candidates = fetch_yc_jobs() + fetch_wellfound_jobs()
    sent = load_sent()
    new = [j for j in candidates if j["link"] not in sent]

    if not new:
        print("No new jobs today.")
        return

    html = format_email(new)
    send_email(html)

    sent.update(j["link"] for j in new)
    save_sent(sent)


# === SCHEDULE DAILY ===
schedule.every(1).hours.do(job_runner)

print("🕒 Scheduler started; will run every hour")
job_runner()  # Run once immediately

while True:
    schedule.run_pending()
    time.sleep(60)
