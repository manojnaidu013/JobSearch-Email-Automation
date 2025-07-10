# Job Search Automation - Gmail Integration

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Gmail API](https://img.shields.io/badge/Gmail-API-red.svg)](https://developers.google.com/gmail/api)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**An intelligent job search automation tool that monitors top job platforms and delivers personalized job alerts directly to your Gmail inbox every 30 minutes.**

## 🎯 Overview

This automation system continuously scans multiple job platforms and sends curated job opportunities directly to your Gmail based on your preferred roles, experience level, and custom filters. Never miss a job opportunity again with this smart, hands-free job hunting assistant.

## 🚀 Key Features

### Multi-Platform Job Scraping
- Monitors top job platforms: **Naukri**, **Internshala**, **Indeed**, **Glassdoor**, and more
- Fetches fresh job postings every **30 minutes**
- Eliminates duplicate listings across platforms
- Covers both Indian and international job markets

### Role-Based Job Filtering
- **UI/UX Designer** - Creative and user experience roles
- **Data Analyst** - Analytics and business intelligence positions
- **Data Scientist** - Machine learning and advanced analytics roles
- **Software Engineer** - Full-stack and backend development opportunities
- **Full Stack Developer** - End-to-end web development positions
- **Additional Roles** - Easily configurable for other tech positions

### Smart Filtering System
- ⏰ **Time-based filters:** Jobs posted in the past 24 hours
- 🎓 **Experience level:** Internships, Entry-level, Mid-level options
- 💰 **Salary range:** Customizable salary brackets
- 📍 **Location preferences:** Remote, hybrid, or specific cities
- 🛠️ **Skills matching:** Filters based on required technical skills
- 🏢 **Company type:** Startups, MNCs, product companies, etc.

### Automated Gmail Delivery
- Clean, formatted job alerts sent directly to your inbox
- Organized email structure with job title, company, salary, and apply links
- Customizable email frequency and format
- Separate emails for different job categories

## 🛠️ Technical Stack

### Web Scraping & Data Processing
- **Python** with BeautifulSoup/Selenium for web scraping
- **Pandas** for data cleaning and filtering
- **Regular expressions** for text processing and skill matching

### Email Integration
- **Gmail API** for secure email sending
- **HTML email templates** for professional formatting
- **OAuth 2.0** authentication for Gmail access

### Automation & Scheduling
- **Cron jobs/Task Scheduler** for 30-minute intervals
- Error handling and retry mechanisms
- Logging system for monitoring scraping activities

### Data Management
- **SQLite/CSV** for storing job data and preventing duplicates
- Configurable settings file for easy customization
- Data validation and cleaning processes

## 📊 Supported Job Platforms

| Platform | Description |
|----------|-------------|
| **Naukri.com** | India's largest job portal |
| **Internshala** | Internships and entry-level positions |
| **Indeed** | Global job search engine |
| **Glassdoor** | Company reviews and job listings |
| **LinkedIn Jobs** | Professional networking platform |
| **AngelList** | Startup and tech company jobs |
| **Freshersworld** | Entry-level opportunities |

## ⚙️ Configuration Options

```python
# Example configuration
JOB_ROLES = [
    "UI/UX Designer",
    "Data Analyst", 
    "Data Scientist",
    "Software Engineer",
    "Full Stack Developer"
]

FILTERS = {
    "time_posted": "24_hours",
    "experience_level": ["internship", "entry_level"],
    "salary_range": "3-8 LPA",
    "location": ["Remote", "Bangalore", "Mumbai"],
    "required_skills": ["Python", "React", "SQL"]
}

EMAIL_SETTINGS = {
    "frequency": "30_minutes",
    "max_jobs_per_email": 10,
    "email_format": "html"
}
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Gmail account with API access
- Internet connection for web scraping

## 🎯 Benefits

### Time Efficiency
- ⏱️ Saves 2-3 hours daily of manual job searching
- 🔄 Eliminates need to visit multiple job portals
- 🎯 Automated filtering reduces irrelevant job noise

### Never Miss Opportunities
- 🚨 Real-time job alerts for fresh postings
- 🌐 Covers multiple platforms simultaneously
- 🎛️ Customizable filters ensure relevant matches

### Professional Advantage
- 🏃‍♂️ Early application submission for new postings
- 🤖 Consistent job search without manual effort
- 📊 Better organization of job opportunities

## 📊 Sample Email Output

```
Subject: 🎯 New Job Opportunities - UI/UX Designer (5 Jobs Found)

Dear Job Seeker,

Here are the latest job opportunities matching your criteria:

🎨 UI/UX Designer - TechCorp Solutions
📍 Bangalore, Remote
💰 4-6 LPA
📅 Posted: 2 hours ago
🔗 Apply Now: [Link]

🎨 Senior UX Designer - StartupXYZ
📍 Mumbai, Hybrid
💰 6-10 LPA
📅 Posted: 5 hours ago
🔗 Apply Now: [Link]

...

Happy Job Hunting!
Your Job Search Automation Bot
```

## 📈 Future Enhancements

- [ ] Resume auto-submission for matched jobs
- [ ] Interview scheduling integration
- [ ] Salary trend analysis and reporting
- [ ] Mobile app for job alerts management
- [ ] Machine learning for better job matching
- [ ] WhatsApp/Telegram integration
- [ ] Job application tracking dashboard
- [ ] Company research automation

## 🛡️ Privacy & Security

- All job data is stored locally
- Gmail API uses OAuth 2.0 for secure authentication
- No personal information is shared with third parties
- Scraping follows robots.txt guidelines

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all job platforms for providing public job listings
- Gmail API for reliable email delivery
- Python community for excellent scraping libraries

**⭐ Star this repository if you find it helpful for your job search automation needs!**

*This project demonstrates skills in web scraping, API integration, automation, and practical problem-solving for career development.*

---

Made with ❤️ by S.Manoj Naidu
