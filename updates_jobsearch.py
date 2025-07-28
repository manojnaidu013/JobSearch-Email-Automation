"""
🎯 INDIAN JOB TRACKER WITH EMAIL NOTIFICATIONS

📧 SETUP INSTRUCTIONS:
1. Replace email credentials in the main() function:
   - from_email: Your Gmail address (sender)
   - password: Your Gmail App Password (NOT regular password)
   - to_email: Where to send job alerts (can be same or different email)

2. Generate Gmail App Password:
   - Go to Google Account → Security → 2-Step Verification
   - Generate App Password → Select "Mail" → Copy 16-digit code
   - Use this code as 'password' in config

3. Customize job searches:
   - Change 'query' to your desired job titles
   - Change 'location' to your preferred Indian cities
   - Select platforms: 'naukri', 'internshala', 'indeed_india', 'foundit', 'shine'

4. Run: python indian_job_tracker.py
"""

import requests
import smtplib
import json
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import schedule
import logging
from typing import List, Dict, Set
import hashlib
import os
from dataclasses import dataclass, asdict
import sqlite3
from bs4 import BeautifulSoup
import re
import urllib.parse
import random

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class JobPosting:
    title: str
    company: str
    location: str
    url: str
    platform: str
    posted_date: str
    description: str = ""
    salary: str = ""
    job_type: str = ""
    experience: str = ""
    
    def to_dict(self):
        return asdict(self)
    
    def get_hash(self):
        """Generate unique hash for job posting"""
        unique_string = f"{self.title}_{self.company}_{self.location}_{self.platform}"
        return hashlib.md5(unique_string.encode()).hexdigest()

class JobDatabase:
    def __init__(self, db_name="indian_job_postings.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash TEXT UNIQUE,
                title TEXT,
                company TEXT,
                location TEXT,
                url TEXT,
                platform TEXT,
                posted_date TEXT,
                description TEXT,
                salary TEXT,
                job_type TEXT,
                experience TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def job_exists(self, job_hash: str) -> bool:
        """Check if job already exists in database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM jobs WHERE hash = ?", (job_hash,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def add_job(self, job: JobPosting):
        """Add new job to database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO jobs (hash, title, company, location, url, platform, posted_date, description, salary, job_type, experience)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job.get_hash(), job.title, job.company, job.location, 
                job.url, job.platform, job.posted_date, job.description, 
                job.salary, job.job_type, job.experience
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

class EmailNotifier:
    def __init__(self, smtp_server: str, smtp_port: int, email: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password
    
    def send_email(self, to_email: str, subject: str, body: str, jobs: List[JobPosting]):
        """Send email notification with job postings"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Create HTML email body
            html_body = self.create_html_body(jobs)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def create_html_body(self, jobs: List[JobPosting]) -> str:
        """Create HTML email body with job listings"""
        # Categorize jobs for better presentation
        uiux_jobs = [job for job in jobs if any(keyword in job.title.lower() for keyword in ['ui', 'ux', 'designer', 'design', 'visual', 'graphic', 'product design'])]
        data_jobs = [job for job in jobs if any(keyword in job.title.lower() for keyword in ['data', 'analyst', 'research', 'sql', 'power bi', 'tableau', 'business analyst'])]
        internship_jobs = [job for job in jobs if any(keyword in job.title.lower() for keyword in ['intern', 'trainee', 'fresher', 'entry', 'junior', 'graduate'])]
        other_jobs = [job for job in jobs if job not in uiux_jobs and job not in data_jobs and job not in internship_jobs]
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .job-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: #f9f9f9; }}
                .job-title {{ color: #2c3e50; font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
                .job-company {{ color: #34495e; font-size: 16px; margin-bottom: 5px; }}
                .job-location {{ color: #7f8c8d; font-size: 14px; margin-bottom: 5px; }}
                .job-platform {{ color: #3498db; font-size: 14px; font-weight: bold; margin-bottom: 10px; }}
                .job-description {{ color: #2c3e50; font-size: 14px; margin-bottom: 10px; }}
                .job-url {{ color: #e74c3c; text-decoration: none; font-weight: bold; }}
                .job-url:hover {{ text-decoration: underline; }}
                .header {{ background-color: #3498db; color: white; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 20px; }}
                .footer {{ margin-top: 30px; text-align: center; color: #7f8c8d; font-size: 12px; }}
                .experience {{ color: #e67e22; font-weight: bold; }}
                .salary {{ color: #27ae60; font-weight: bold; }}
                .category-header {{ background-color: #34495e; color: white; padding: 15px; text-align: center; border-radius: 8px; margin: 20px 0 10px 0; }}
                .uiux-card {{ border-left: 5px solid #e74c3c; }}
                .data-card {{ border-left: 5px solid #3498db; }}
                .internship-card {{ border-left: 5px solid #27ae60; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-item {{ text-align: center; padding: 10px; background-color: #ecf0f1; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎨📊 UI/UX & Data Jobs in India!</h1>
                <p>Found {len(jobs)} new job postings matching your criteria</p>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <h3>🎨 {len(uiux_jobs)}</h3>
                    <p>UI/UX Design Jobs</p>
                </div>
                <div class="stat-item">
                    <h3>📊 {len(data_jobs)}</h3>
                    <p>Data Analysis Jobs</p>
                </div>
                <div class="stat-item">
                    <h3>🎓 {len(internship_jobs)}</h3>
                    <p>Internships & Entry Level</p>
                </div>
                <div class="stat-item">
                    <h3>📄 {len(other_jobs)}</h3>
                    <p>Other Opportunities</p>
                </div>
            </div>
        """
        
        # UI/UX Design Jobs Section
        if uiux_jobs:
            html += '<div class="category-header">🎨 UI/UX DESIGN OPPORTUNITIES</div>'
            for job in uiux_jobs:
                html += f"""
                <div class="job-card uiux-card">
                    <div class="job-title">{job.title}</div>
                    <div class="job-company">🏢 {job.company}</div>
                    <div class="job-location">📍 {job.location}</div>
                    <div class="job-platform">🌐 Platform: {job.platform}</div>
                    {f'<div class="experience">💼 Experience: {job.experience}</div>' if job.experience else ''}
                    {f'<div class="salary">💰 {job.salary}</div>' if job.salary else ''}
                    {f'<div class="job-description">📝 {job.description[:200]}...</div>' if job.description else ''}
                    <div style="margin-top: 10px;">
                        <a href="{job.url}" class="job-url" target="_blank">📄 View Job Posting</a>
                    </div>
                    <div style="color: #95a5a6; font-size: 12px; margin-top: 5px;">Posted: {job.posted_date}</div>
                </div>
                """
        
        # Data Analysis Jobs Section
        if data_jobs:
            html += '<div class="category-header">📊 DATA ANALYSIS OPPORTUNITIES</div>'
            for job in data_jobs:
                html += f"""
                <div class="job-card data-card">
                    <div class="job-title">{job.title}</div>
                    <div class="job-company">🏢 {job.company}</div>
                    <div class="job-location">📍 {job.location}</div>
                    <div class="job-platform">🌐 Platform: {job.platform}</div>
                    {f'<div class="experience">💼 Experience: {job.experience}</div>' if job.experience else ''}
                    {f'<div class="salary">💰 {job.salary}</div>' if job.salary else ''}
                    {f'<div class="job-description">📝 {job.description[:200]}...</div>' if job.description else ''}
                    <div style="margin-top: 10px;">
                        <a href="{job.url}" class="job-url" target="_blank">📄 View Job Posting</a>
                    </div>
                    <div style="color: #95a5a6; font-size: 12px; margin-top: 5px;">Posted: {job.posted_date}</div>
                </div>
                """
        
        # Internships & Entry Level Jobs Section
        if internship_jobs:
            html += '<div class="category-header">🎓 INTERNSHIPS & ENTRY LEVEL OPPORTUNITIES</div>'
            for job in internship_jobs:
                html += f"""
                <div class="job-card internship-card">
                    <div class="job-title">{job.title}</div>
                    <div class="job-company">🏢 {job.company}</div>
                    <div class="job-location">📍 {job.location}</div>
                    <div class="job-platform">🌐 Platform: {job.platform}</div>
                    {f'<div class="experience">💼 Experience: {job.experience}</div>' if job.experience else ''}
                    {f'<div class="salary">💰 {job.salary}</div>' if job.salary else ''}
                    {f'<div class="job-description">📝 {job.description[:200]}...</div>' if job.description else ''}
                    <div style="margin-top: 10px;">
                        <a href="{job.url}" class="job-url" target="_blank">📄 View Job Posting</a>
                    </div>
                    <div style="color: #95a5a6; font-size: 12px; margin-top: 5px;">Posted: {job.posted_date}</div>
                </div>
                """
        
        # Other Jobs Section
        if other_jobs:
            html += '<div class="category-header">📄 OTHER OPPORTUNITIES</div>'
            for job in other_jobs:
                html += f"""
                <div class="job-card">
                    <div class="job-title">{job.title}</div>
                    <div class="job-company">🏢 {job.company}</div>
                    <div class="job-location">📍 {job.location}</div>
                    <div class="job-platform">🌐 Platform: {job.platform}</div>
                    {f'<div class="experience">💼 Experience: {job.experience}</div>' if job.experience else ''}
                    {f'<div class="salary">💰 {job.salary}</div>' if job.salary else ''}
                    {f'<div class="job-description">📝 {job.description[:200]}...</div>' if job.description else ''}
                    <div style="margin-top: 10px;">
                        <a href="{job.url}" class="job-url" target="_blank">📄 View Job Posting</a>
                    </div>
                    <div style="color: #95a5a6; font-size: 12px; margin-top: 5px;">Posted: {job.posted_date}</div>
                </div>
                """
        
        html += """
            <div class="footer">
                <p>🎨 Focus: UI/UX Design | 📊 Data Analysis | 🎓 Internships & Entry Level</p>
                <p>This is an automated job alert for your targeted roles. Happy job hunting! 🚀</p>
            </div>
        </body>
        </html>
        """
        return html

class IndianJobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def scrape_naukri(self, query: str, location: str = "", limit: int = 10) -> List[JobPosting]:
        """Scrape Naukri.com job postings"""
        jobs = []
        try:
            encoded_query = urllib.parse.quote(query)
            encoded_location = urllib.parse.quote(location) if location else ""
            
            url = f"https://www.naukri.com/{encoded_query}-jobs"
            if encoded_location:
                url += f"-in-{encoded_location}"
            
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('article', class_='jobTuple')
            
            for card in job_cards[:limit]:
                try:
                    title_elem = card.find('a', class_='title')
                    title = title_elem.get_text(strip=True) if title_elem else "N/A"
                    job_url = title_elem.get('href', '') if title_elem else ""
                    if job_url and not job_url.startswith('http'):
                        job_url = f"https://www.naukri.com{job_url}"
                    
                    company_elem = card.find('a', class_='subTitle')
                    company = company_elem.get_text(strip=True) if company_elem else "N/A"
                    
                    location_elem = card.find('span', class_='ellipsis fleft locWdth')
                    location = location_elem.get_text(strip=True) if location_elem else "N/A"
                    
                    exp_elem = card.find('span', class_='ellipsis fleft expwdth')
                    experience = exp_elem.get_text(strip=True) if exp_elem else "N/A"
                    
                    salary_elem = card.find('span', class_='ellipsis fleft salaryWdth')
                    salary = salary_elem.get_text(strip=True) if salary_elem else "N/A"
                    
                    desc_elem = card.find('span', class_='job-description')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    jobs.append(JobPosting(
                        title=title,
                        company=company,
                        location=location,
                        url=job_url,
                        platform="Naukri",
                        posted_date="Recent",
                        description=description,
                        salary=salary,
                        experience=experience
                    ))
                except Exception as e:
                    logger.error(f"Error parsing Naukri job: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Naukri: {str(e)}")
        
        return jobs
    
    def scrape_internshala(self, query: str, location: str = "", limit: int = 10) -> List[JobPosting]:
        """Scrape Internshala job postings"""
        jobs = []
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://internshala.com/jobs/{encoded_query}-jobs"
            if location:
                url += f"-in-{urllib.parse.quote(location)}"
            
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('div', class_='internship_meta')
            
            for card in job_cards[:limit]:
                try:
                    title_elem = card.find('h3', class_='job-internship-name')
                    title = title_elem.get_text(strip=True) if title_elem else "N/A"
                    
                    link_elem = card.find('a', href=True)
                    job_url = f"https://internshala.com{link_elem['href']}" if link_elem else ""
                    
                    company_elem = card.find('p', class_='company-name')
                    company = company_elem.get_text(strip=True) if company_elem else "N/A"
                    
                    location_elem = card.find('p', class_='location-names')
                    location = location_elem.get_text(strip=True) if location_elem else "N/A"
                    
                    salary_elem = card.find('span', class_='stipend')
                    salary = salary_elem.get_text(strip=True) if salary_elem else "N/A"
                    
                    jobs.append(JobPosting(
                        title=title,
                        company=company,
                        location=location,
                        url=job_url,
                        platform="Internshala",
                        posted_date="Recent",
                        salary=salary
                    ))
                except Exception as e:
                    logger.error(f"Error parsing Internshala job: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Internshala: {str(e)}")
        
        return jobs
    
    def scrape_indeed_india(self, query: str, location: str = "", limit: int = 10) -> List[JobPosting]:
        """Scrape Indeed India job postings"""
        jobs = []
        try:
            encoded_query = urllib.parse.quote(query)
            encoded_location = urllib.parse.quote(location) if location else ""
            
            url = f"https://in.indeed.com/jobs?q={encoded_query}&l={encoded_location}"
            
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            for card in job_cards[:limit]:
                try:
                    title_elem = card.find('h2', class_='jobTitle')
                    title_link = title_elem.find('a') if title_elem else None
                    title = title_link.get_text(strip=True) if title_link else "N/A"
                    job_url = f"https://in.indeed.com{title_link['href']}" if title_link else ""
                    
                    company_elem = card.find('span', class_='companyName')
                    company = company_elem.get_text(strip=True) if company_elem else "N/A"
                    
                    location_elem = card.find('div', {'data-testid': 'job-location'})
                    location = location_elem.get_text(strip=True) if location_elem else "N/A"
                    
                    salary_elem = card.find('span', class_='salary-snippet')
                    salary = salary_elem.get_text(strip=True) if salary_elem else "N/A"
                    
                    desc_elem = card.find('div', class_='job-snippet')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    jobs.append(JobPosting(
                        title=title,
                        company=company,
                        location=location,
                        url=job_url,
                        platform="Indeed India",
                        posted_date="Recent",
                        description=description,
                        salary=salary
                    ))
                except Exception as e:
                    logger.error(f"Error parsing Indeed India job: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Indeed India: {str(e)}")
        
        return jobs
    
    def scrape_foundit(self, query: str, location: str = "", limit: int = 10) -> List[JobPosting]:
        """Scrape Foundit (formerly Monster India) job postings"""
        jobs = []
        try:
            encoded_query = urllib.parse.quote(query)
            encoded_location = urllib.parse.quote(location) if location else ""
            
            url = f"https://www.foundit.in/jobs/{encoded_query}-jobs"
            if encoded_location:
                url += f"-in-{encoded_location}"
            
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('div', class_='srpResultCardContainer')
            
            for card in job_cards[:limit]:
                try:
                    title_elem = card.find('h3', class_='jobTitle')
                    title_link = title_elem.find('a') if title_elem else None
                    title = title_link.get_text(strip=True) if title_link else "N/A"
                    job_url = title_link.get('href', '') if title_link else ""
                    
                    company_elem = card.find('span', class_='companyName')
                    company = company_elem.get_text(strip=True) if company_elem else "N/A"
                    
                    location_elem = card.find('span', class_='locationsContainer')
                    location = location_elem.get_text(strip=True) if location_elem else "N/A"
                    
                    exp_elem = card.find('span', class_='experience')
                    experience = exp_elem.get_text(strip=True) if exp_elem else "N/A"
                    
                    salary_elem = card.find('span', class_='salary')
                    salary = salary_elem.get_text(strip=True) if salary_elem else "N/A"
                    
                    jobs.append(JobPosting(
                        title=title,
                        company=company,
                        location=location,
                        url=job_url,
                        platform="Foundit",
                        posted_date="Recent",
                        salary=salary,
                        experience=experience
                    ))
                except Exception as e:
                    logger.error(f"Error parsing Foundit job: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Foundit: {str(e)}")
        
        return jobs
    
    def scrape_shine(self, query: str, location: str = "", limit: int = 10) -> List[JobPosting]:
        """Scrape Shine.com job postings"""
        jobs = []
        try:
            encoded_query = urllib.parse.quote(query)
            encoded_location = urllib.parse.quote(location) if location else ""
            
            url = f"https://www.shine.com/jobs/{encoded_query}-jobs"
            if encoded_location:
                url += f"-in-{encoded_location}"
            
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('div', class_='jobCard')
            
            for card in job_cards[:limit]:
                try:
                    title_elem = card.find('h2', class_='jobTitle')
                    title_link = title_elem.find('a') if title_elem else None
                    title = title_link.get_text(strip=True) if title_link else "N/A"
                    job_url = title_link.get('href', '') if title_link else ""
                    
                    company_elem = card.find('div', class_='companyName')
                    company = company_elem.get_text(strip=True) if company_elem else "N/A"
                    
                    location_elem = card.find('div', class_='jobLocation')
                    location = location_elem.get_text(strip=True) if location_elem else "N/A"
                    
                    exp_elem = card.find('div', class_='experience')
                    experience = exp_elem.get_text(strip=True) if exp_elem else "N/A"
                    
                    jobs.append(JobPosting(
                        title=title,
                        company=company,
                        location=location,
                        url=job_url,
                        platform="Shine",
                        posted_date="Recent",
                        experience=experience
                    ))
                except Exception as e:
                    logger.error(f"Error parsing Shine job: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Shine: {str(e)}")
        
        return jobs

class IndianJobTracker:
    def __init__(self, config: Dict):
        self.config = config
        self.database = JobDatabase()
        self.scraper = IndianJobScraper()
        self.email_notifier = EmailNotifier(
            smtp_server=config['email']['smtp_server'],
            smtp_port=config['email']['smtp_port'],
            email=config['email']['from_email'],
            password=config['email']['password']
        )
    
    def track_jobs(self):
        """Main job tracking function"""
        logger.info("Starting Indian job tracking session...")
        new_jobs = []
        
        for search_config in self.config['job_searches']:
            query = search_config['query']
            location = search_config.get('location', '')
            platforms = search_config.get('platforms', ['naukri', 'internshala', 'indeed_india', 'foundit', 'shine'])
            
            logger.info(f"Searching for: {query} in {location or 'All locations'}")
            
            for platform in platforms:
                try:
                    logger.info(f"Scraping {platform}...")
                    
                    if platform.lower() == 'naukri':
                        jobs = self.scraper.scrape_naukri(query, location, limit=15)
                    elif platform.lower() == 'internshala':
                        jobs = self.scraper.scrape_internshala(query, location, limit=15)
                    elif platform.lower() == 'indeed_india':
                        jobs = self.scraper.scrape_indeed_india(query, location, limit=15)
                    elif platform.lower() == 'foundit':
                        jobs = self.scraper.scrape_foundit(query, location, limit=15)
                    elif platform.lower() == 'shine':
                        jobs = self.scraper.scrape_shine(query, location, limit=15)
                    else:
                        continue
                    
                    # Filter and add new jobs
                    for job in jobs:
                        if job.title != "N/A" and job.company != "N/A":
                            if not self.database.job_exists(job.get_hash()):
                                if self.database.add_job(job):
                                    new_jobs.append(job)
                                    logger.info(f"New job found: {job.title} at {job.company} on {job.platform}")
                
                except Exception as e:
                    logger.error(f"Error tracking jobs on {platform}: {str(e)}")
                
                # Add delay between platforms to avoid rate limiting
                time.sleep(random.uniform(3, 7))
        
        # Send email notification if new jobs found
        if new_jobs:
            self.send_notification(new_jobs)
        else:
            logger.info("No new jobs found in this session")
    
    def send_notification(self, jobs: List[JobPosting]):
        """Send email notification for new jobs"""
        # Count jobs by category
        uiux_count = len([job for job in jobs if any(keyword in job.title.lower() for keyword in ['ui', 'ux', 'designer', 'design', 'visual', 'graphic', 'product design'])])
        data_count = len([job for job in jobs if any(keyword in job.title.lower() for keyword in ['data', 'analyst', 'research', 'sql', 'power bi', 'tableau', 'business analyst'])])
        internship_count = len([job for job in jobs if any(keyword in job.title.lower() for keyword in ['intern', 'trainee', 'fresher', 'entry', 'junior', 'graduate'])])
        
        subject = f"🎨📊 {len(jobs)} New Jobs: {uiux_count} UI/UX | {data_count} Data | {internship_count} Internships"
        body = f"Found {len(jobs)} new job postings in your target areas: UI/UX Design, Data Analysis, and Internships."
        
        success = self.email_notifier.send_email(
            to_email=self.config['email']['to_email'],
            subject=subject,
            body=body,
            jobs=jobs
        )
        
        if success:
            logger.info(f"Successfully sent email with {len(jobs)} new jobs ({uiux_count} UI/UX, {data_count} Data, {internship_count} Internships)")
        else:
            logger.error("Failed to send email notification")

def main():
    # ============= EMAIL CONFIGURATION - UPDATE THESE VALUES =============
    config = {
        'email': {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'from_email': 'manojsomarowthu123@gmail.com',     # 📧 PUT YOUR GMAIL HERE
            'password': 'yptq ivvi ryxp jdei',                # 🔑 PUT YOUR APP PASSWORD HERE
            'to_email': 'manojnaidusomarowthu@gmail.com'      # 📬 PUT RECEIVER EMAIL HERE #yptq ivvi ryxp jdei
        },
        # ============= JOB SEARCH CONFIGURATION FOR UI/UX & DATA ROLES =============
        'job_searches': [
            # UI/UX Designer Roles - PRIMARY FOCUS
            {
                'query': 'ui ux designer',                     # 🎨 PRIMARY FOCUS
                'location': 'Hyderabad',
                'platforms': ['naukri', 'internshala', 'indeed_india', 'foundit', 'shine']
            },
            {
                'query': 'ux designer',                        # 🎨 UX SPECIFIC
                'location': 'Bangalore',
                'platforms': ['naukri', 'internshala', 'indeed_india', 'foundit']
            },
            {
                'query': 'ui designer',                        # 🎨 UI SPECIFIC
                'location': 'Mumbai',
                'platforms': ['naukri', 'indeed_india', 'shine', 'foundit']
            },
            {
                'query': 'product designer',                   # 🎨 PRODUCT DESIGN
                'location': 'Chennai',
                'platforms': ['naukri', 'internshala', 'indeed_india']
            },
            {
                'query': 'visual designer',                    # 🎨 VISUAL DESIGN
                'location': 'Pune',
                'platforms': ['naukri', 'indeed_india', 'foundit']
            },
            {
                'query': 'web designer',                       # 🎨 WEB DESIGN
                'location': 'Delhi',
                'platforms': ['internshala', 'naukri', 'shine']
            },
            {
                'query': 'graphic designer',                   # 🎨 GRAPHIC DESIGN
                'location': 'Gurgaon',
                'platforms': ['naukri', 'indeed_india', 'foundit']
            },
            
            # Data Analyst & Related Roles - SECONDARY FOCUS
            {
                'query': 'data analyst',                       # 📊 DATA ANALYST
                'location': 'Hyderabad',
                'platforms': ['naukri', 'internshala', 'indeed_india', 'foundit']
            },
            {
                'query': 'data scientist',                     # 📊 DATA SCIENTIST
                'location': 'Bangalore',
                'platforms': ['naukri', 'indeed_india', 'shine']
            },
            {
                'query': 'business analyst',                   # 📊 BUSINESS ANALYST
                'location': 'Mumbai',
                'platforms': ['naukri', 'foundit', 'indeed_india']
            },
            {
                'query': 'data engineer',                      # 📊 DATA ENGINEER
                'location': 'Chennai',
                'platforms': ['naukri', 'indeed_india', 'shine']
            },
            {
                'query': 'research analyst',                   # 📊 RESEARCH ANALYST
                'location': 'Pune',
                'platforms': ['naukri', 'internshala', 'indeed_india']
            },
            {
                'query': 'market research analyst',            # 📊 MARKET RESEARCH
                'location': 'Delhi',
                'platforms': ['naukri', 'indeed_india', 'foundit']
            },
            {
                'query': 'sql analyst',                        # 📊 SQL ANALYST
                'location': 'Noida',
                'platforms': ['naukri', 'indeed_india', 'shine']
            },
            {
                'query': 'power bi analyst',                   # 📊 POWER BI
                'location': 'Hyderabad',
                'platforms': ['naukri', 'indeed_india', 'foundit']
            },
            {
                'query': 'tableau analyst',                    # 📊 TABLEAU
                'location': 'Bangalore',
                'platforms': ['naukri', 'indeed_india', 'shine']
            },
            
            # Internships & Entry Level - ALL TYPES
            {
                'query': 'internship',                         # 🎓 ALL INTERNSHIPS
                'location': 'Hyderabad',
                'platforms': ['internshala', 'naukri', 'indeed_india']
            },
            {
                'query': 'fresher jobs',                       # 🎓 FRESHER JOBS
                'location': 'Bangalore',
                'platforms': ['naukri', 'internshala', 'indeed_india']
            },
            {
                'query': 'entry level',                        # 🎓 ENTRY LEVEL
                'location': 'Mumbai',
                'platforms': ['naukri', 'indeed_india', 'foundit']
            },
            {
                'query': 'graduate trainee',                   # 🎓 GRADUATE TRAINEE
                'location': 'Chennai',
                'platforms': ['naukri', 'indeed_india', 'shine']
            },
            {
                'query': 'trainee',                            # 🎓 TRAINEE POSITIONS
                'location': 'Pune',
                'platforms': ['naukri', 'internshala', 'indeed_india']
            },
            {
                'query': 'junior',                             # 🎓 JUNIOR POSITIONS
                'location': 'Delhi',
                'platforms': ['naukri', 'indeed_india', 'foundit']
            }
        ]
    }
    
    # Initialize job tracker
    tracker = IndianJobTracker(config)
    
    # Schedule job tracking every 10 minutes
    schedule.every(30).minutes.do(tracker.track_jobs)
    
    print("🚀 UI/UX & Data Jobs Tracker Started!")
    print("📧 Email notifications enabled - Every 10 minutes")
    print("🎯 PRIMARY FOCUS: UI/UX Designer roles")
    print("🎯 SECONDARY FOCUS: Data Analyst & related roles")
    print("🎯 TERTIARY FOCUS: All internships & entry-level positions")
    print("🇮🇳 Searching: Naukri, Internshala, Indeed India, Foundit, Shine")
    print("📍 Locations: Hyderabad, Bangalore, Mumbai, Chennai, Pune, Delhi, Gurgaon, Noida")
    print("⏰ Checking every 10 minutes for new opportunities...")
    print("🎨 UI/UX Roles: UI Designer, UX Designer, Product Designer, Visual Designer, Web Designer, Graphic Designer")
    print("📊 Data Roles: Data Analyst, Data Scientist, Business Analyst, Research Analyst, SQL Analyst, Power BI, Tableau")
    print("🎓 Entry Level: Internships, Fresher Jobs, Trainee positions, Graduate roles")
    print("Press Ctrl+C to stop")
    
    # Run initial check
    tracker.track_jobs()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
