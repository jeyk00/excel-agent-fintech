# Deployment Guide for Excel Financial Agent

This guide explains how to deploy your **Excel Financial Agent** to the web using **Streamlit Community Cloud**.

## 1. Architecture Overview

You asked: *"Where to deploy backend?"*

**Answer**: You do NOT need a separate backend deployment.
Your application is a cohesive unit where the "frontend" (Streamlit interface) and the "backend" (Python logic, data processing, AI calls) run together on the same server. When you deploy the Streamlit app, you are deploying the backend too.

## 2. Prerequisites

Your project is ready for deployment. We have created a `requirements.txt` file which Streamlit needs to install dependencies.

Ensure your code is pushed to GitHub:
```bash
git add requirements.txt
git commit -m "Prepare for deployment"
git push origin <your-branch-name>
```

## 3. Deploying to Streamlit Cloud

1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Log in with your GitHub account.
3.  Click **"New app"**.
4.  **Repository**: Select your repo `jeyk00/excel-agent-fintech`.
5.  **Branch**: Select your working branch.
6.  **Main file path**: Enter `src/app.py`.
    *   *Note: It is important to point to the file inside `src/` as that is your entry point.*
7.  Click **"Deploy!"**.

## 4. Configuring API Keys (Secrets) 🔑

This is the most critical step to ensure it works with **your** API keys.

1.  Once the app is deploying (or after it fails initially due to missing keys), go to your app's dashboard.
2.  Click the **Settings** menu (three dots in the top right corner of the app view) -> **Settings**.
3.  Go to the **Secrets** tab.
4.  Paste your environment variables here in TOML format. It should look like the contents of your `.env` file but formatted slightly differently if needed (though straight key=value pairs usually work, TOML uses `key = "value"`).

**Example format:**

```toml
OPENAI_API_KEY = "sk-..."
GEMINI_API_KEY = "..."
LLAMA_CLOUD_API_KEY = "llx-..."
```

5.  Click **Save**. The app will restart automatically with access to these keys.

## 5. Sharing with Your Client

*   Once deployed, you will get a URL like `https://excel-agent-fintech.streamlit.app`.
*   You can share this URL directly with your client.
