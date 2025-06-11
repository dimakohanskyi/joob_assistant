import logging
from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from settings.logging_config import configure_logging
from handlers.start_handler import start_handler
from handlers.profile_handlers.user_profile_handler import profile_handler
from handlers.profile_handlers.create_profile import create_account
from handlers.profile_handlers.experience_handler import add_user_experience, process_experience_input
from handlers.profile_handlers.hard_skills_handler import add_hard_skills, process_adding_hard_skills
from handlers.profile_handlers.soft_skills_handler import add_soft_skills, process_adding_soft_skills
from handlers.profile_handlers.education_handler import add_education, process_adding_education
from handlers.profile_handlers.languages_handler import add_languages, process_adding_languages
from handlers.profile_handlers.projects_handler import add_projects, process_adding_projects
from handlers.profile_handlers.git_hub_handler import add_github, process_adding_github
from handlers.profile_handlers.linkedin_handler import add_linkedin, process_adding_linkedin
from handlers.profile_handlers.email_handler import add_email, process_adding_email
from handlers.job_handlers.get_job_item_analyse import job_analyse_handler, process_job_url
from handlers.job_handlers.add_job_url import add_job_item_url, process_job_item_url
from handlers.job_handlers.set_job_item_status import set_job_item_status
from handlers.job_handlers.show_job_items import show_job_items


from handlers.menu_handler import main_menu_handler, get_add_menu_handler

from states.profile_states.experience_state import ExperienceState
from states.profile_states.hard_skills_state import HardSkillsState
from states.profile_states.soft_skills_state import SoftSkillsState
from states.profile_states.education_state import EducationState
from states.profile_states.languages_state import LanguagesState
from states.profile_states.projects_state import ProjectsState
from states.profile_states.git_hub_state import GitHubState
from states.profile_states.linkedin_state import LinkedInState
from states.profile_states.email_state import EmailState
from states.job_states.job_analyse_state import JobAnalyseState
from states.job_states.job_item_url_state import JobUrlState




configure_logging()
logger = logging.getLogger(__name__)



router = Router()


router.message.register(start_handler, CommandStart())
router.message.register(
    process_experience_input,
    StateFilter(ExperienceState.waiting_for_experience, ExperienceState.waiting_for_update_confirmation)
)
router.message.register(
    process_adding_hard_skills,
    StateFilter(HardSkillsState.waiting_for_hard_skills, HardSkillsState.waiting_for_update_confirmation)
)
router.message.register(
    process_adding_soft_skills,
    StateFilter(SoftSkillsState.waiting_for_soft_skills, SoftSkillsState.waiting_for_update_confirmation)
)
router.message.register(
    process_adding_education,
    StateFilter(EducationState.waiting_for_education, EducationState.waiting_for_update_confirmation)
)

router.message.register(
    process_adding_languages, 
    StateFilter(LanguagesState.waiting_for_languages, LanguagesState.waiting_for_update_confirmation)
)

router.message.register(
    process_adding_projects, 
    StateFilter(ProjectsState.waiting_for_projects, ProjectsState.waiting_for_update_confirmation)
)

router.message.register(
    process_adding_github, 
    StateFilter(GitHubState.waiting_for_github, GitHubState.waiting_for_update_confirmation)
)

router.message.register(
    process_adding_linkedin, 
    StateFilter(LinkedInState.waiting_for_linkedin, LinkedInState.waiting_for_update_confirmation)
)

router.message.register(
    process_adding_email, 
    StateFilter(EmailState.waiting_for_email, EmailState.waiting_for_update_confirmation)
)

router.message.register(
    process_job_url,
    StateFilter(JobAnalyseState.waiting_for_url)
)

router.message.register(
    process_job_item_url,
    StateFilter(JobUrlState.waiting_for_item_url)
)




@router.callback_query()
async def handle_callback(callback_query: CallbackQuery, state: FSMContext):
    command = callback_query.data

    try:
        if command == "profile":
            await profile_handler(callback_query)
        elif command == "create_account":
            await create_account(callback_query)
        elif command == "main_menu":
            await main_menu_handler(callback_query)
        elif command == "job_keyboard":
            await get_add_menu_handler(callback_query)
        elif command == "add_user_experience":
            await add_user_experience(callback_query, state)
        elif command == "profile_hard_skills":
            await add_hard_skills(callback_query, state)
        elif command == "profile_soft_skills":
            await add_soft_skills(callback_query, state)
        elif command == "profile_education":
            await add_education(callback_query, state)
        elif command == "profile_languages":
            await add_languages(callback_query, state)
        elif command == "profile_projects":
            await add_projects(callback_query, state)
        elif command == "profile_github":
            await add_github(callback_query, state)
        elif command == "profile_linkedin":
            await add_linkedin(callback_query, state)
        elif command == "profile_email":
            await add_email(callback_query, state)
        elif command == "analyse_job_item":
            await job_analyse_handler(callback_query, state)
        elif command == "add_job_url":
            await add_job_item_url(callback_query, state)
        elif command == "add_job_status":
            await set_job_item_status(callback_query)

        elif command == "show_jobs":
            await show_job_items(callback_query)



        # elif command.startswith("show_job_"):
        #     await show_job_item_details(callback_query)
        # elif command.startswith("change_status_"):
        #     await show_status_update(callback_query)
        # elif command.startswith("change_priority_"):
        #     await show_priority_update(callback_query)
        # elif command.startswith("set_status_"):
        #     await update_job_status(callback_query)
        # elif command.startswith("set_priority_"):
        #     await update_job_priority(callback_query)

    except Exception as ex:
        logger.error(f"Error executing command - {command}")
        print(ex)
