# Gmail Spam Delete Agent

This project provides a conversational AI agent that helps you clean up your Gmail inbox by identifying and deleting promotional and social media emails.

## Features

- **Conversational Interface:** Chat with the agent in natural language to manage your inbox.
- **Customizable Cleaning:** Specify criteria for emails to delete, such as labels, date ranges, and sender.
- **Dry-Run Mode:** Simulate the deletion process without actually removing any emails to ensure accuracy.
- **Automated Cron Jobs:** Set up a workflow to automatically run the cleaning script on a schedule.

## Setup

### 1. Prerequisites

- Python 3.12 or higher
- `uv` package manager (or `pip`)
- Google Cloud Project with the Gmail API enabled

### 2. Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/gmail-spam-delete-agent.git
    cd gmail-spam-delete-agent
    ```

2.  **Create a virtual environment and install dependencies:**

    ```bash
    uv venv
    uv sync
    ```

### 3. Google API Credentials

1.  **Create OAuth Client Credentials:**
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project or select an existing one.
    - Enable the **Gmail API**.
    - Go to **Credentials**, click **Create Credentials**, and select **OAuth client ID**.
    - Choose **Desktop app** as the application type.
    - Download the JSON file and save it as `credentials/client_secret.json` in the project directory.

2.  **Set up Environment Variables:**
    - Create a `.env` file in the project root.
    - Add your Gemini API key to the `.env` file:

      ```
      GOOGLE_API_KEY=your_gemini_api_key
      ```

3.  **Generate User Token:**
    - Run the following command to authorize the application and generate a `token.json` file:

      ```bash
      uv run gmail-auth
      ```

## Usage

### Interactive Cleaning

To start a conversational session with the agent, run:

```bash
uv run gmail-clean-inbox-swarm
```

You can then chat with the agent to clean your inbox. For example:

- "Show me unread promotional emails."
- "Delete emails older than 30 days from 'promotions' or 'social'."
- "Find all emails from 'example@example.com' and delete them."

### Automated Cleaning

This project includes a script to automatically delete promotional and social emails.

**To run the script:**

```bash
uv run python src/gmail_spam_delete_agent/delete_promotional_emails.py
```

**To perform a dry run (simulate deletion without actually removing emails):**

```bash
uv run python src/gmail_spam_delete_agent/delete_promotional_emails.py --dry-run
```

### Automated Cron Job

You can set up a GitHub Actions workflow to run the cleaning script on a schedule. A sample workflow file is provided at `.github/workflows/cleanup.yml`.

**To use the workflow:**

1.  Create a `.github/workflows` directory in your project.
2.  Copy the `cleanup.yml` file into the directory.
3.  Commit and push the changes to your repository.

The workflow is configured to run every day at midnight. You can customize the schedule by editing the `cron` expression in the `cleanup.yml` file.