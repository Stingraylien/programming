Python 3.11.1 (v3.11.1:a7a450f84a, Dec  6 2022, 15:24:06) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> import os
... from google.oauth2.credentials import Credentials
... from googleapiclient.discovery import build
... from googleapiclient.errors import HttpError
... 
... # 定義函數判斷資料夾是否為空
... def is_folder_empty(folder_id, service):
...     query = f"'{folder_id}' in parents and trashed = false and mimeType = 'application/vnd.google-apps.folder'"
...     results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
...     files = results.get("files", [])
...     return len(files) == 0
... 
      # 取得驗證資訊
creds = Credentials.from_authorized_user_file('credentials.json')

# 建立Google Drive API客戶端
service = build('drive', 'v3', credentials=creds)

# 取得根目錄資料夾的ID
root_folder_query = "mimeType='application/vnd.google-apps.folder' and name='root' and trashed = false"
root_folder_results = service.files().list(q=root_folder_query, fields="nextPageToken, files(id, name)").execute()
root_folder_id = root_folder_results.get("files", [])[0].get("id")

# 取得所有的資料夾，開始搜尋並刪除空資料夾
query = "mimeType='application/vnd.google-apps.folder' and trashed = false"
results = service.files().list(q=query, fields="nextPageToken, files(id, name, parents)").execute()
items = results.get("files", [])

for item in items:
    # 如果是根目錄或者還有父資料夾，跳過
    if item["id"] == root_folder_id or "parents" not in item:
        continue
        
    # 如果這個資料夾是空的，刪除它
    if is_folder_empty(item["id"], service):
        try:
            service.files().delete(fileId=item["id"]).execute()
            print(f"刪除資料夾 {item['name']} ({item['id']}) 成功")
        except HttpError as error:
            print(f"刪除資料夾 {item['name']} ({item['id']}) 失敗: {error}")
