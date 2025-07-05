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
            data['name'] = self.driver.find_element(By.CSS_SELECTOR, 'h1.text-heading-xlarge').text
        except Exception:
            data['name'] = ''
        try:
            data['headline'] = self.driver.find_element(By.CSS_SELECTOR, 'div.text-body-medium.break-words').text
        except Exception:
            data['headline'] = ''
        try:
            data['location'] = self.driver.find_element(By.CSS_SELECTOR, 'span.text-body-small.inline.t-black--light.break-words').text
        except Exception:
            data['location'] = ''
        # Experience, education, and skills extraction (simplified)
        data['experiences'] = self._extract_experiences()
        data['education'] = self._extract_education()
        data['skills'] = self._extract_skills()
        self.driver.quit()
        return data

    def _extract_experiences(self):
        experiences = []
        try:
            exp_sections = self.driver.find_elements(By.CSS_SELECTOR, 'section#experience-section li')
            for exp in exp_sections:
                try:
                    title = exp.find_element(By.CSS_SELECTOR, 'h3').text
                except Exception:
                    title = ''
                try:
                    company = exp.find_element(By.CSS_SELECTOR, 'p.pv-entity__secondary-title').text
                except Exception:
                    company = ''
                try:
                    date_range = exp.find_element(By.CSS_SELECTOR, 'h4.pv-entity__date-range span:nth-child(2)').text
                except Exception:
                    date_range = ''
                try:
                    description = exp.find_element(By.CSS_SELECTOR, 'div.pv-entity__extra-details').text
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

    def _extract_education(self):
        education = []
        try:
            edu_sections = self.driver.find_elements(By.CSS_SELECTOR, 'section#education-section li')
            for edu in edu_sections:
                try:
                    school = edu.find_element(By.CSS_SELECTOR, 'h3').text
                except Exception:
                    school = ''
                try:
                    degree = edu.find_element(By.CSS_SELECTOR, 'span.pv-entity__comma-item').text
                except Exception:
                    degree = ''
                try:
                    date_range = edu.find_element(By.CSS_SELECTOR, 'p.pv-entity__dates span:nth-child(2)').text
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

    def _extract_skills(self):
        skills = []
        try:
            skill_elements = self.driver.find_elements(By.CSS_SELECTOR, 'span.pv-skill-category-entity__name-text')
            for skill in skill_elements:
                skills.append(skill.text)
        except Exception:
            pass
        return skills 