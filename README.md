# release-notes-bot

# Jira Release Notes Generator

A Python script that automates the generation of release notes for Jira issues using GPT-4. It supports both individual user stories and epics, with interactive approval workflow for epic stories.

## Features

- Generates release notes for Jira user stories using GPT-4
- Handles both individual stories and epics
- For epics:
  - Lists all non-closed user stories
  - Processes each story individually
  - Interactive approval workflow
- Updates Jira custom fields with approved release notes
- Supports skipping stories and early exit

## Prerequisites

- Python 3.9+
- Jira API access
- OpenAI API access

## Installation

1. Clone the repository
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - `JIRA_API_TOKEN`: Your Jira API token
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `JIRA_BASE_URL`: Your Jira base URL (e.g., `https://your-jira-instance.atlassian.net`)
   - `JIRA_PROJECT_KEY`: The key of the project you want to process
   - `JIRA_EPIC_FIELD_ID`: The ID of the custom field used for epics
   - `JIRA_STORY_FIELD_ID`: The ID of the custom field used for user stories
   - `JIRA_RELEASE_NOTES_FIELD_ID`: The ID of the custom field used for storing release notes

## Usage

Run the script with a Jira issue key:

```bash
python release_notes.py PROJ-123
```

### For Individual User Stories
- The script will generate release notes and update the specified Jira field

### For Epics
- Lists all non-closed user stories in the epic
- For each story:
  - Generates release notes
  - Shows the generated notes
  - Prompts for action:
    - `Y` (Yes): Approve and update Jira
    - `N` (No): Reject and move to next story
    - `S` (Skip): Skip to next story
    - `E` (Exit): Exit the script completely

## Example Output

```
📥 Fetching description for PROJ-123...
📋 Issue Type: Epic

Found 5 non-closed stories in this epic.

[1/5] Processing: PROJ-124: Implement login feature
🤖 Generating release notes using GPT-4...

📋 Generated Release Notes:
------------------------
Added user authentication functionality with:
- Email/password login
- OAuth2 support for Google
- Remember me option
------------------------

Do you want to approve these release notes? (Y)es/(N)o/(S)kip/(E)xit:
```

## Error Handling

- Validates Jira issue types
- Handles API errors gracefully
- Provides feedback for invalid inputs

## Notes

- The script only processes stories that are not in 'Closed' or 'Done' status
- Release notes are generated using GPT-4 based on the story description
- Progress is shown when processing multiple stories in an epic
- A summary of approved stories is shown at the end

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Your chosen license]
