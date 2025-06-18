import logging
from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from src.settings.logging_config import configure_logging
from src.handlers.start_handler import start_handler

from src.handlers.profile_handlers.user_profile_handler import profile_handler
from src.handlers.profile_handlers.create_profile import create_account
from src.handlers.profile_handlers.experience_handler import add_experience, process_adding_experience, process_experience_confirmation
from src.handlers.profile_handlers.hard_skills_handler import add_hard_skills, process_adding_hard_skills, process_hard_skills_confirmation
from src.handlers.profile_handlers.soft_skills_handler import add_soft_skills, process_adding_soft_skills, process_soft_skills_confirmation
from src.handlers.profile_handlers.education_handler import add_education, process_adding_education, process_education_confirmation
from src.handlers.profile_handlers.languages_handler import add_languages, process_adding_languages, process_languages_confirmation
from src.handlers.profile_handlers.projects_handler import add_projects, process_adding_projects, process_projects_confirmation
from src.handlers.profile_handlers.git_hub_handler import add_github, process_adding_github, process_github_confirmation
from src.handlers.profile_handlers.linkedin_handler import add_linkedin, process_adding_linkedin, process_linkedin_confirmation
from src.handlers.profile_handlers.email_handler import add_email, process_adding_email, process_email_confirmation

from src.handlers.job_handlers.get_job_item_analyse import job_analyse_handler, process_job_url
from src.handlers.job_handlers.add_job_url import add_job_item_url, process_job_item_url
from src.handlers.job_handlers.show_job_items import show_job_items
from src.handlers.job_handlers.job_status_handler import job_status_handler, process_adding_job_status
from src.handlers.job_handlers.job_priority_handler import job_priority_handler, process_adding_job_priority
from src.handlers.job_handlers.job_additional_info_handler import job_additional_info_handler, process_additional_info
from src.handlers.job_handlers.finish_adding_handler import finish_adding_job
from src.handlers.job_handlers.get_update_job_handler import (
    get_update_job_handler,
    get_job_item_info_handler,
    update_job_item_handler,
    process_get_job_item_info,
    process_update_job_item_info
)
from src.handlers.job_handlers.job_ai_summary_handler import job_ai_summary_handler

from src.handlers.menu_handler import main_menu_handler

from src.states.profile_states.experience_state import ExperienceState
from src.states.profile_states.hard_skills_state import HardSkillsState
from src.states.profile_states.soft_skills_state import SoftSkillsState
from src.states.profile_states.education_state import EducationState
from src.states.profile_states.languages_state import LanguagesState
from src.states.profile_states.projects_state import ProjectsState
from src.states.profile_states.git_hub_state import GitHubState
from src.states.profile_states.linkedin_state import LinkedInState
from src.states.profile_states.email_state import EmailState
from src.states.job_states.job_analyse_state import JobAnalyseState
from src.states.job_states.job_item_url_state import JobUrlState
from src.states.job_states.job_get_update_state import JobGetUpdateState


configure_logging()
logger = logging.getLogger(__name__)


router = Router()

router.message.register(start_handler, CommandStart())



router.message.register(
    process_adding_experience,
    StateFilter(ExperienceState.waiting_for_experience)
)
router.message.register(
    process_adding_hard_skills,
    StateFilter(HardSkillsState.waiting_for_hard_skills)
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

router.message.register(
    process_additional_info,
    StateFilter(JobUrlState.waiting_for_additional_info)
)

router.message.register(
    process_get_job_item_info,
    StateFilter(JobGetUpdateState.waiting_for_item_id)
)

router.message.register(
    process_update_job_item_info,
    StateFilter(JobGetUpdateState.waiting_for_update_item_id)
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
        elif command == "add_user_experience":
            await add_experience(callback_query, state)
        elif command in ["confirm_experience_update", "cancel_experience_update", "create_profile"]:
            await process_experience_confirmation(callback_query, state)
        elif command == "profile_hard_skills":
            await add_hard_skills(callback_query, state)
        elif command in ["confirm_hard_skills_update", "cancel_hard_skills_update", "create_profile"]:
            await process_hard_skills_confirmation(callback_query, state)
        elif command == "profile_soft_skills":
            await add_soft_skills(callback_query, state)
        elif command in ["confirm_soft_skills_update", "cancel_soft_skills_update"]:
            await process_soft_skills_confirmation(callback_query, state)
        elif command == "profile_education":
            await add_education(callback_query, state)
        elif command in ["confirm_education_update", "cancel_education_update"]:
            await process_education_confirmation(callback_query, state)
        elif command == "profile_languages":
            await add_languages(callback_query, state)
        elif command in ["confirm_languages_update", "cancel_languages_update"]:
            await process_languages_confirmation(callback_query, state)
        elif command == "profile_projects":
            await add_projects(callback_query, state)
        elif command in ["confirm_projects_update", "cancel_projects_update"]:
            await process_projects_confirmation(callback_query, state)
        elif command == "profile_github":
            await add_github(callback_query, state)
        elif command in ["confirm_github_update", "cancel_github_update"]:
            await process_github_confirmation(callback_query, state)
        elif command == "profile_linkedin":
            await add_linkedin(callback_query, state)
        elif command in ["confirm_linkedin_update", "cancel_linkedin_update"]:
            await process_linkedin_confirmation(callback_query, state)
        elif command == "profile_email":
            await add_email(callback_query, state)
        elif command in ["confirm_email_update", "cancel_email_update"]:
            await process_email_confirmation(callback_query, state)
        elif command == "analyse_job_item":
            await job_analyse_handler(callback_query, state)
        elif command == "add_job_url":
            await add_job_item_url(callback_query, state)
        elif command == "show_jobs":
            await show_job_items(callback_query)
        elif command == "add_job_status":
            await job_status_handler(callback_query, state)
        elif command.startswith("set_status_"):
            await process_adding_job_status(callback_query, state)
        elif command == "add_job_priority":
            await job_priority_handler(callback_query, state)
        elif command.startswith("set_priority_"):
            await process_adding_job_priority(callback_query, state)
        elif command == "add_job_additional_info":
            await job_additional_info_handler(callback_query, state)
        elif command == "add_job_ai_summary":
            await job_ai_summary_handler(callback_query, state)
        elif command == "finish_adding_job":
            await finish_adding_job(callback_query, state)
        elif command == "get_job_item":
            await get_update_job_handler(callback_query)
        elif command == "get_job_item_info":
            await get_job_item_info_handler(callback_query, state)
        elif command == "update_job_item":
            await update_job_item_handler(callback_query, state)

    except Exception as ex:
        logger.error(f"Error executing command - {command}")
        logger.error(str(ex))
        await callback_query.message.answer("❌ An error occurred. Please try again.")
