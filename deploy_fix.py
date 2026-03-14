import os
import requests
import base64

# CONFIGURATION
TOKEN = "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" # Provided by user
REPO = "adityaiitian123/climaPy"
FILE_PATH = "frontend/components/sidebar.py"
LOCAL_FILE = r"c:\Users\ASUS\OneDrive\Desktop\Py-Climax\frontend\components\sidebar.py"

def deploy_via_api():
    print(f"🚀 Attempting API deployment for {FILE_PATH}...")
    
    # 1. Get current file data (to get the SHA)
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch file info: {response.json()}")
        return

    sha = response.json().get("sha")
    
    # 2. Read local content
    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    
    # 3. Update file
    data = {
        "message": "fix(sidebar): ultra-robust unit detection (API Deploy)",
        "content": encoded_content,
        "sha": sha,
        "branch": "main"
    }
    
    put_response = requests.put(url, headers=headers, json=data)
    
    if put_response.status_code in [200, 201]:
        print("✅ SUCCESS! The file has been updated via GitHub API.")
        print("Streamlit Cloud should redeploy momentarily.")
    else:
        print(f"❌ Failed to update file: {put_response.json()}")

if __name__ == "__main__":
    deploy_via_api()
