from aiogram.types import CallbackQuery
import logging

from src.databese.models import User, Profile
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.profile_keyboard import get_create_profile_keyboard


configure_logging()
logger = logging.getLogger(__name__)


async def profile_handler(callback: CallbackQuery):
    async for session in get_db():
        try:
            user = await User.get_user(tg_user_id=callback.from_user.id, session=session)
            
            if user:
                profile = await Profile.get_user_profile(session=session, user_id=user.id)
                experience = f"{profile.user_experience} years" if profile.user_experience else "Not specified"
                languages = profile.user_languages if profile.user_languages else "Not specified"
                hard_skills = profile.hard_skills if profile.hard_skills else "Not specified"
                soft_skills = profile.soft_skills if profile.soft_skills else "Not specified"
                education = profile.education if profile.education else "Not specified"
                projects = profile.projects if profile.projects else "Not specified"
                github = profile.user_git_hub if profile.user_git_hub else "Not specified"
                linkedin = profile.user_linkedin if profile.user_linkedin else "Not specified"

                profile_message = (
                    f"👤 <b>Professional Profile</b>\n\n"
                    f"<b>Basic Information:</b>\n"
                    f"• Username: {user.tg_user_name}\n"
                    f"• Email: {user.user_login}\n"
                    f"• Profile Created: {user.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"<b>Professional Details:</b>\n"
                    f"• Experience: {experience}\n"
                    f"• Languages: {languages}\n"
                    f"• Hard Skills: {hard_skills}\n"
                    f"• Soft Skills: {soft_skills}\n"
                    f"• Education: {education}\n"
                    f"• Projects: {projects}\n\n"
                    f"<b>Professional Links:</b>\n"
                    f"• GitHub: {github}\n"
                    f"• LinkedIn: {linkedin}"
                )
                
                await callback.message.edit_caption(
                    caption=profile_message,
                    reply_markup=get_create_profile_keyboard(),
                    parse_mode="HTML"
                )
            else:
                await callback.message.edit_caption(
                    caption="❌ Sorry, we couldn't find your profile data.\n"
                    "Please try creating a profile first or contact support if you believe this is an error.",
                    reply_markup=get_create_profile_keyboard()
                )
        except Exception as ex:
            logger.error(f"Error in profile_handler: {str(ex)}")
            await callback.message.edit_caption(
                caption="❌ Please try again later or contact support if the problem persists.",
                reply_markup=get_create_profile_keyboard()
            )























# data = {
#     'id': '3403649346253045671',
#     'from_user': {
#         'id': 792473868,
#         'is_bot': False,
#         'first_name': 'Dima',
#         'last_name': None,
#         'username': 'dima_dkt',
#         'language_code': 'en',
#         'is_premium': None,
#         'added_to_attachment_menu': None,
#         'can_join_groups': None,
#         'can_read_all_group_messages': None,
#         'supports_inline_queries': None,
#         'can_connect_to_business': None,
#         'has_main_web_app': None
#     },
#     'chat_instance': '1063630834179484397',
#     'message': {
#         'message_id': 57,
#         'date': '2025-06-06 10:22:52+00:00',
#         'chat': {
#             'id': 792473868,
#             'type': 'private',
#             'title': None,
#             'username': 'dima_dkt',
#             'first_name': 'Dima',
#             'last_name': None,
#             'is_forum': None,
#             'accent_color_id': None,
#             'active_usernames': None,
#             'available_reactions': None,
#             'background_custom_emoji_id': None,
#             'bio': None,
#             'birthdate': None,
#             'business_intro': None,
#             'business_location': None,
#             'business_opening_hours': None,
#             'can_set_sticker_set': None,
#             'custom_emoji_sticker_set_name': None,
#             'description': None,
#             'emoji_status_custom_emoji_id': None,
#             'emoji_status_expiration_date': None,
#             'has_aggressive_anti_spam_enabled': None,
#             'has_hidden_members': None,
#             'has_private_forwards': None,
#             'has_protected_content': None,
#             'has_restricted_voice_and_video_messages': None,
#             'has_visible_history': None,
#             'invite_link': None,
#             'join_by_request': None,
#             'join_to_send_messages': None,
#             'linked_chat_id': None,
#             'location': None,
#             'message_auto_delete_time': None,
#             'permissions': None,
#             'personal_chat': None,
#             'photo': None,
#             'pinned_message': None,
#             'profile_accent_color_id': None,
#             'profile_background_custom_emoji_id': None,
#             'slow_mode_delay': None,
#             'sticker_set_name': None,
#             'unrestrict_boost_count': None
#         },
#         'message_thread_id': None,
#         'from_user': {
#             'id': 7611898178,
#             'is_bot': True,
#             'first_name': 'jobb_assistent',
#             'last_name': None,
#             'username': 'jobb_assistent_bot',
#             'language_code': None,
#             'is_premium': None,
#             'added_to_attachment_menu': None,
#             'can_join_groups': None,
#             'can_read_all_group_messages': None,
#             'supports_inline_queries': None,
#             'can_connect_to_business': None,
#             'has_main_web_app': None
#         },
#         'sender_chat': None,
#         'sender_boost_count': None,
#         'sender_business_bot': None,
#         'business_connection_id': None,
#         'forward_origin': None,
#         'is_topic_message': None,
#         'is_automatic_forward': None,
#         'reply_to_message': None,
#         'external_reply': None,
#         'quote': None,
#         'reply_to_story': None,
#         'via_bot': None,
#         'edit_date': None,
#         'has_protected_content': None,
#         'is_from_offline': None,
#         'media_group_id': None,
#         'author_signature': None,
#         'paid_star_count': None,
#         'text': None,
#         'entities': None,
#         'link_preview_options': None,
#         'effect_id': None,
#         'animation': None,
#         'audio': None,
#         'document': None,
#         'paid_media': None,
#         'photo': [
#             {
#                 'file_id': 'AgACAgIAAxkDAAMFaD3zMAh5Y7Qt7JwKm5ATCNsrZUIAAjvyMRsSbOlJfPeaGUb7n4wBAAMCAANzAAM2BA',
#                 'file_unique_id': 'AQADO_IxGxJs6Ul4',
#                 'width': 90,
#                 'height': 90,
#                 'file_size': 1927
#             },
#             {
#                 'file_id': 'AgACAgIAAxkDAAMFaD3zMAh5Y7Qt7JwKm5ATCNsrZUIAAjvyMRsSbOlJfPeaGUb7n4wBAAMCAANtAAM2BA',
#                 'file_unique_id': 'AQADO_IxGxJs6Uly',
#                 'width': 320,
#                 'height': 320,
#                 'file_size': 25934
#             },
#             {
#                 'file_id': 'AgACAgIAAxkDAAMFaD3zMAh5Y7Qt7JwKm5ATCNsrZUIAAjvyMRsSbOlJfPeaGUb7n4wBAAMCAAN4AAM2BA',
#                 'file_unique_id': 'AQADO_IxGxJs6Ul9',
#                 'width': 800,
#                 'height': 800,
#                 'file_size': 133751
#             },
#             {
#                 'file_id': 'AgACAgIAAxkDAAMFaD3zMAh5Y7Qt7JwKm5ATCNsrZUIAAjvyMRsSbOlJfPeaGUb7n4wBAAMCAAN5AAM2BA',
#                 'file_unique_id': 'AQADO_IxGxJs6Ul-',
#                 'width': 1024,
#                 'height': 1024,
#                 'file_size': 214858
#             }
#         ],
#         'sticker': None,
#         'story': None,
#         'video': None,
#         'video_note': None,
#         'voice': None,
#         'caption': "Welcome back! You're already logged in to Joob Assistant\n\n👋 Hey there! I'm Joob Assistant — your smart job-hunting buddy 💼🤖\n\nHere's what I can help you with:\n👤 Build your profile\n🔍 Analyze job posts with AI\n✉️ Generate custom cover letters\n📂 Track your applications\n📄 Save multiple CVs\n📊 Organize your job search like a pro\n\nLet's land your next job together! 🚀",
#         'caption_entities': None,
#         'show_caption_above_media': None,
#         'has_media_spoiler': None,
#         'contact': None,
#         'dice': None,
#         'game': None,
#         'poll': None,
#         'venue': None,
#         'location': None,
#         'new_chat_members': None,
#         'left_chat_member': None,
#         'new_chat_title': None,
#         'new_chat_photo': None,
#         'delete_chat_photo': None,
#         'group_chat_created': None,
#         'supergroup_chat_created': None,
#         'channel_chat_created': None,
#         'message_auto_delete_timer_changed': None,
#         'migrate_to_chat_id': None,
#         'migrate_from_chat_id': None,
#         'pinned_message': None,
#         'invoice': None,
#         'successful_payment': None,
#         'refunded_payment': None,
#         'users_shared': None,
#         'chat_shared': None,
#         'gift': None,
#         'unique_gift': None,
#         'connected_website': None,
#         'write_access_allowed': None,
#         'passport_data': None,
#         'proximity_alert_triggered': None,
#         'boost_added': None,
#         'chat_background_set': None,
#         'forum_topic_created': None,
#         'forum_topic_edited': None,
#         'forum_topic_closed': None,
#         'forum_topic_reopened': None,
#         'general_forum_topic_hidden': None,
#         'general_forum_topic_unhidden': None,
#         'giveaway_created': None,
#         'giveaway': None,
#         'giveaway_winners': None,
#         'giveaway_completed': None,
#         'paid_message_price_changed': None,
#         'video_chat_scheduled': None,
#         'video_chat_started': None,
#         'video_chat_ended': None,
#         'video_chat_participants_invited': None,
#         'web_app_data': None,
#         'reply_markup': {
#             'inline_keyboard': [
#                 [
#                     {
#                         'text': '👤 User Profile',
#                         'url': None,
#                         'callback_data': 'profile',
#                         'web_app': None,
#                         'login_url': None,
#                         'switch_inline_query': None,
#                         'switch_inline_query_current_chat': None,
#                         'switch_inline_query_chosen_chat': None,
#                         'copy_text': None,
#                         'callback_game': None,
#                         'pay': None
#                     }
#                 ],
#                 [
#                     {
#                         'text': '👤 Create Profile',
#                         'url': None,
#                         'callback_data': 'create_profile',
#                         'web_app': None,
#                         'login_url': None,
#                         'switch_inline_query': None,
#                         'switch_inline_query_current_chat': None,
#                         'switch_inline_query_chosen_chat': None,
#                         'copy_text': None,
#                         'callback_game': None,
#                         'pay': None
#                     }
#                 ]
#             ]
#         },
#         'forward_date': None,
#         'forward_from': None,
#         'forward_from_chat': None,
#         'forward_from_message_id': None,
#         'forward_sender_name': None,
#         'forward_signature': None,
#         'user_shared': None
#     },
#     'inline_message_id': None,
#     'data': 'profile',
#     'game_short_name': None
# } 

