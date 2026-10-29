# 🔄 Git Repository Mirror Automation

This repository contains an automated GitHub Actions workflow and a Python script designed to completely clone (mirror) any target Git repository and push its entire history (all branches and commits) to a **new, private repository** on your GitHub account.

This tool is especially useful for securely backing up or copying sensitive source code, such as Payment Gateway integrations, while ensuring the new repository remains strictly private.

---

## ✨ Features

- **Automated Repository Creation**: Automatically creates a new repository in your GitHub account using the GitHub API.
- **Private by Default**: Secures your code by making the newly created repository `Private` automatically.
- **Full History Clone**: Uses `git clone --mirror` to ensure every single branch, tag, and commit history is copied perfectly.
- **Zero Local Setup**: Runs entirely in the cloud via GitHub Actions.
- **Dynamic Inputs**: Allows you to specify the target Git URL and the new repository name right before running the action.

---

## 📂 File Structure

Ensure your repository has the exact following structure for the automation to work:

```text
📦 your-main-repo
 ┣ 📂 .github
 ┃ ┗ 📂 workflows
 ┃   ┗ 📜 copy-repo.yml      # The GitHub Actions workflow file
 ┣ 📂 Copy Git
 ┃ ┗ 📜 main.py              # The core Python script that handles API calls & Git commands
 ┗ 📜 README.md              # This file
