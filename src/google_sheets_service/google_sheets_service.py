# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# import logging

# from src.settings.config import CREDENTIALS_FILE_PATH, GOOGLE_SERVICE_EMAIL
# from src.databese.models import User, Jobb
# from src.databese.settings import get_db
# from src.settings.logging_config import configure_logging


# configure_logging()
# logger = logging.getLogger(__name__)




# class GoogleSheetsService:

#     def __init__(self, credentials_path, google_service_email):
#         self.credentials_path = credentials_path
#         self.google_service_email = google_service_email
#         # self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
#         self.SCOPES = [
#             'https://www.googleapis.com/auth/spreadsheets',
#             'https://www.googleapis.com/auth/drive'  
#         ]
#         self.service = self._initialize_service()


#     def _initialize_service(self):
#         credentials = service_account.Credentials.from_service_account_file(
#             self.credentials_path, 
#             scopes=self.SCOPES
#         )
#         return build('sheets', 'v4', credentials=credentials)



#     async def create_sheet_for_user(self, tg_user_id: int):
#         try:
#             async for session in get_db():
#                 existing_url = await self.get_user_sheet(tg_user_id)
#                 if existing_url:
#                     return existing_url

#                 user = await User.get_user(tg_user_id, session)
#                 if not user:
#                     logger.error(f"User not found with tg_id: {tg_user_id}")
#                     return 

#                 spreadsheet = {
#                     'properties': {
#                         'title': f"Job Tracker - User {tg_user_id}"
#                     }
#                 }
                
#                 sheet = self.service.spreadsheets().create(body=spreadsheet).execute()
#                 sheet_id = sheet.get('spreadsheetId')

#                 drive_service = build('drive', 'v3', credentials=self.service._credentials)

#                 service_account_permission = {
#                     'type': 'user',
#                     'role': 'writer',
#                     'emailAddress': self.google_service_email
#                 }
                
                
#                 drive_service.permissions().create(
#                     fileId=sheet_id,
#                     body=service_account_permission,
#                     fields='id'
#                 ).execute()

#                 user_permission = {
#                     'type': 'user',
#                     'role': 'reader',
#                     'emailAddress': user.user_login
#                 }

#                 drive_service.permissions().create(
#                     fileId=sheet_id,
#                     body=user_permission,
#                     fields='id'
#                 ).execute()
                
#                 sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
                
#                 user.google_sheet_id = sheet_id
#                 user.google_sheet_url = sheet_url
#                 await session.commit()
                
#                 return sheet_url

#         except Exception as ex:
#             logger.error("error with creation google user sheet")
#             return None
        



#     async def get_user_sheet(self, tg_user_id: int):
#         try:
#             async for session in get_db():
#                 user = await User.get_user(tg_user_id, session)

#                 if not user:
#                     logger.error(f"User not found with tg_id: {tg_user_id}")
#                     return 

#                 if user.google_sheet_id:
#                     return f"https://docs.google.com/spreadsheets/d/{user.google_sheet_id}"

#         except Exception as ex:
#             logger.error("error with creation google user sheet")











#     # async def update_sheet_data(self, user: User, data: dict):
#     #     # Update sheet with new data
#     #     # Handle errors
#     #     pass