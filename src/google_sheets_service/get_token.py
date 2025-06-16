# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# import pickle
# import os
# import sys

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# def get_token(credentials_file: str = 'src/google_sheets_service/sec.json') -> None:

#     try:
#         if not os.path.exists(credentials_file):
#             print(f"Error: Credentials file '{credentials_file}' not found!")
#             print("Please make sure you have downloaded your service account credentials")
#             sys.exit(1)

#         print("Creating credentials from service account...")
#         credentials = service_account.Credentials.from_service_account_file(
#             credentials_file, scopes=SCOPES)

#         print("Building Google Sheets service...")
#         service = build('sheets', 'v4', credentials=credentials)
        
#         print("\nAuthentication successful! 🎉")
#         print("You can now use this service in your bot.")
#         return service

#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         print("Please make sure you have:")
#         print("1. Enabled Google Sheets API in Google Cloud Console")
#         print("2. Downloaded the correct service account credentials file")
#         print("3. Installed all required packages")
#         sys.exit(1)

# if __name__ == '__main__':
#     print("Starting Google Sheets authentication...")
#     try:
#         service = get_token()
#         print("\nNext steps:")
#         print("1. Use this service to interact with Google Sheets")
#         print("2. Make sure to share your sheets with the service account email")
#     except KeyboardInterrupt:
#         print("\nAuthentication cancelled by user.")
#         sys.exit(0)

