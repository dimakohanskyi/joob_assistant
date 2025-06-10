from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from settings.logging_config import configure_logging
import logging


configure_logging()
logger = logging.getLogger(__name__)


load_dotenv()
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
client = OpenAI(api_key=OPEN_AI_KEY)



async def analyse_job_url(job_url: str):

    prompt = "You are an expert career assistant designed to help job seekers by summarizing job descriptions accurately and concisely. Your task is to take a provided job description and create a short, structured summary that captures all critical information. The summary must include:"
    
    try:
        response = requests.get(job_url)  

        if not response:
            logger.error(f"error with parsing url -- {job_url}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')  
        job_content = soup.get_text()
        cleaned_content = ' '.join(job_content.split())

        response = client.responses.create(
            model="gpt-4o",
            instructions=prompt,
            input=cleaned_content,
        )
        if not response:
            logger.error("error with getting responce from ai modal")
            return
        
        return response.output_text
    except Exception as ex:
        logger.error(f"Erorr of genereting job item summary - {ex}")




    
