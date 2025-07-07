import os
import time
from typing import Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

class LinkedInScraper:
    def __init__(self, email: str = None, password: str = None):
        self.email = email or LINKEDIN_EMAIL
        self.password = password or LINKEDIN_PASSWORD
        self.driver = None

    def _init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)

    def login(self):
        self._init_driver()
        self.driver.get('https://www.linkedin.com/login')
        time.sleep(2)
        email_input = self.driver.find_element(By.ID, 'username')
        password_input = self.driver.find_element(By.ID, 'password')
        email_input.send_keys(self.email)
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(3)

    def scrape_profile(self, profile_url: str = "https://www.linkedin.com/in/me/") -> Dict[str, Any]:
        self.login()
        self.driver.get(profile_url)
        time.sleep(3)
        data = {}
        try:
            # Name: robust selector for modern LinkedIn
            data['name'] = self.driver.find_element(By.CSS_SELECTOR, 'div.text-heading-xlarge, h1.text-heading-xlarge, h1').text
        except Exception:
            data['name'] = ''
        try:
            # Headline: robust selector
            data['headline'] = self.driver.find_element(By.CSS_SELECTOR, 'div.text-body-medium.break-words, div.text-body-medium, .text-body-medium').text
        except Exception:
            data['headline'] = ''
        try:
            # Location: robust selector
            data['location'] = self.driver.find_element(By.CSS_SELECTOR, 'span.text-body-small.inline.t-black--light.break-words, .text-body-small.inline.t-black--light, .text-body-small').text
        except Exception:
            data['location'] = ''
        # Experience, education, and skills extraction (modern selectors)
        data['experiences'] = self._extract_experiences_modern()
        data['education'] = self._extract_education_modern()
        data['skills'] = self._extract_skills_modern()
        self.driver.quit()
        return data

    def _extract_experiences_modern(self):
        experiences = []
        try:
            # Modern LinkedIn: experience section is a list of divs with data-section="experience-section"
            exp_sections = self.driver.find_elements(By.CSS_SELECTOR, 'section[data-section="experience-section"] ul li, section[id*="experience"] ul li, .experience__list li')
            for exp in exp_sections:
                try:
                    title = exp.find_element(By.CSS_SELECTOR, 'span[aria-hidden="true"], .t-bold span, .t-bold').text
                except Exception:
                    title = ''
                try:
                    company = exp.find_element(By.CSS_SELECTOR, 'span.t-14.t-normal, .t-normal span, .t-normal').text
                except Exception:
                    company = ''
                try:
                    date_range = exp.find_element(By.CSS_SELECTOR, 'span.t-14.t-normal.t-black--light, .t-black--light span, .t-black--light').text
                except Exception:
                    date_range = ''
                try:
                    description = exp.find_element(By.CSS_SELECTOR, 'div.pv-entity__extra-details, .pvs-list__outer-container, .display-flex.flex-column.full-width').text
                except Exception:
                    description = ''
                experiences.append({
                    'title': title,
                    'company': company,
                    'date_range': date_range,
                    'description': description
                })
        except Exception:
            pass
        return experiences

    def _extract_education_modern(self):
        education = []
        try:
            edu_sections = self.driver.find_elements(By.CSS_SELECTOR, 'section[data-section="education-section"] ul li, section[id*="education"] ul li, .education__list li')
            for edu in edu_sections:
                try:
                    school = edu.find_element(By.CSS_SELECTOR, 'span[aria-hidden="true"], .t-bold span, .t-bold').text
                except Exception:
                    school = ''
                try:
                    degree = edu.find_element(By.CSS_SELECTOR, 'span.t-14.t-normal, .t-normal span, .t-normal').text
                except Exception:
                    degree = ''
                try:
                    date_range = edu.find_element(By.CSS_SELECTOR, 'span.t-14.t-normal.t-black--light, .t-black--light span, .t-black--light').text
                except Exception:
                    date_range = ''
                education.append({
                    'school': school,
                    'degree': degree,
                    'date_range': date_range
                })
        except Exception:
            pass
        return education

    def _extract_skills_modern(self):
        skills = []
        try:
            # Modern LinkedIn: skills are in span elements with .pvs-entity__skill-name or similar
            skill_elements = self.driver.find_elements(By.CSS_SELECTOR, 'span.pvs-entity__skill-name, span[aria-hidden="true"], .skill-entity__skill-name')
            for skill in skill_elements:
                text = skill.text.strip()
                if text and text not in skills:
                    skills.append(text)
        except Exception:
            pass
        return skills 