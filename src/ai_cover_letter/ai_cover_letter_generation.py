from openai import OpenAI
import logging

from src.settings.logging_config import configure_logging
from src.settings.config import OPEN_AI_KEY


configure_logging()
logger = logging.getLogger(__name__)


client = OpenAI(api_key=OPEN_AI_KEY)


async def ai_cover_letter_generation(user_data: dict):
    
    prompt = """
        You are a skilled career coach tasked with writing a concise, authentic job proposal message (100-150 words) to a company, using the provided user profile and job description. The message must:

        1. Feel Human: Use a genuine, conversational tone, avoiding AI clichés (e.g., "excited to reach out"). Reflect the candidate’s unique voice from the user profile.
        2. Professional yet Approachable: Balance professionalism with relatability, avoiding overly formal language.
        3. Highlight Motivation and Fit: Explain the candidate’s motivation for proposing their skills for the role, connecting their experience and skills to the job description and company values.
        4. Unique and Memorable: Use a creative approach (e.g., a brief anecdote or value-driven pitch) to stand out, avoiding generic AI formats.
        5. Avoid AI Detection: Use varied sentences and specific details to ensure the message feels human-written.
        6. Tailored Content: Incorporate details from the user profile (e.g., skills, achievements) and job description (e.g., role, company mission).

        Input Data:
        - User Profile: [Insert user-provided data]
        - Job Description: [Insert job description]

        Output: Provide a plain-text job proposal message with real names and details, no placeholders. Include a simple closing with the candidate’s name.
    """

    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions=prompt,
            # input=cleaned_content,
        )
      
        if not response:
            logger.error("error with getting responce from ai modal")
            return
        
        return response.output_text
    except Exception as ex:
        logger.error(f"Erorr of genereting cover_letter - {ex}")




    
