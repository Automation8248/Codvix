import os
import sys
import subprocess
import requests
import shutil

def main():
    # 1. Inputs fetch karna Action ke environment se
    target_url = os.environ.get("TARGET_GIT_URL")
    new_repo_name = os.environ.get("NEW_REPO_NAME")
    universal_token = os.environ.get("UNIVERSAL_TOKEN")
    github_user = os.environ.get("GITHUB_USER")

    if not universal_token:
        print("Error: UNIVERSAL_TOKEN secret is missing! Repository settings me secret add karein.")
        sys.exit(1)

    # 2. GitHub API se aapke account mein naya Repository create karna
    api_url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {universal_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Gateway source code private rakhna safe rehta hai
    data = {
        "name": new_repo_name,
        "private": True,
        "description": "Payment Gateway Code Repository"
    }

    print(f"Creating new repository '{new_repo_name}' for user '{github_user}'...")
    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code == 201:
        print("✅ Repository created successfully.")
    elif response.status_code == 422:
        print("⚠️ Repository pehle se exist karta hai, hum isme code push karenge.")
    else:
        print(f"❌ Failed to create repo: {response.text}")
        sys.exit(1)

    # 3. Target URL se pura Git Copy (Mirror clone) karna
    clone_dir = "temp_repo_clone"
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir)

    print(f"Cloning from: {target_url} (Mirroring all branches/commits)...")
    subprocess.run(["git", "clone", "--mirror", target_url, clone_dir], check=True)

    # 4. Naye Repo mein sab kuch push karna
    os.chdir(clone_dir)
    
    # Authentication ke liye token URL mein add karna
    new_repo_url = f"https://{github_user}:{universal_token}@github.com/{github_user}/{new_repo_name}.git"

    print(f"Pushing full git history to {new_repo_name}...")
    push_process = subprocess.run(["git", "push", "--mirror", new_repo_url])
    
    if push_process.returncode == 0:
        print("🎉 All done! Pura git repository successfully copy aur save ho gaya hai.")
    else:
        print("❌ Push failed. Please check your UNIVERSAL_TOKEN permissions.")
        sys.exit(1)

if __name__ == "__main__":
    main()
