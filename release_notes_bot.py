import requests
import json
from openai import OpenAI
import sys

# ✅ Configure Jira API Credentials
JIRA_DOMAIN = "snorkelai.atlassian.net"
JIRA_EMAIL = "@snorkel.ai"
JIRA_API_TOKEN = "x"

# ✅ Configure OpenAI API Key
OPENAI_API_KEY = "x"

# ✅ Configure Jira Custom Field ID for Release Notes
RELEASE_NOTES_FIELD = "customfield_10204"  # Hardcoded custom field ID

# ✅ Jira API Headers
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# ✅ Function to Get Jira Issue Description
def get_jira_description(issue_key):
    """Fetches the description and issue type of a Jira issue."""
    url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{issue_key}"
    
    response = requests.get(url, headers=HEADERS, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
    
    if response.status_code == 200:
        issue_data = response.json()
        issue_type = issue_data["fields"]["issuetype"]["name"]
        description = issue_data["fields"].get("description", "No description available.")
        return {"description": description, "issue_type": issue_type}
    else:
        print(f"❌ Failed to fetch issue {issue_key}. Response: {response.text}")
        return None

# ✅ Function to Generate Release Notes using GPT-4 (Updated API)
def generate_release_notes(description):
    """Uses GPT-4 to generate release notes from a Jira issue description."""
    prompt = f"""
    Write concise release notes in 1-2 declarative sentences based on the user story details. Please do not include words such as "in this release" or "users can do".
    Clearly describe the functionality, key features, and benefits without omitting critical details.

    User Story Description:
    {description}

    Release Notes:
    """


    client = OpenAI(
        api_key=OPENAI_API_KEY  # This is the default and can be omitted
    )

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
    )

    return response.choices[0].message.content.strip()

# ✅ Function to Update Jira Custom Field (customfield_10204)
def update_jira_custom_field(issue_key, custom_field_id, new_value):
    """Updates a custom field in a Jira issue."""
    url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{issue_key}"

    # Format the content in Atlassian Document Format
    adf_content = {
        "version": 1,
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": new_value
                    }
                ]
            }
        ]
    }

    payload = {
        "fields": {
            custom_field_id: adf_content
        }
    }

    response = requests.put(
        url,
        headers=HEADERS,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        data=json.dumps(payload)
    )

    if response.status_code == 204:
        print(f"✅ Successfully updated {custom_field_id} in {issue_key}")
    else:
        print(f"❌ Failed to update {issue_key}. Response: {response.text}")

# ✅ Function to Get Epic Stories
def get_epic_stories(epic_key):
    """Fetches all stories linked to an epic that are not Done or Closed."""
    jql = f'parent = {epic_key} AND issuetype in ("Story", "User Story") AND status not in (Closed, Done)'
    url = f"https://{JIRA_DOMAIN}/rest/api/3/search"
    
    params = {
        "jql": jql,
        "fields": "key,summary,status"
    }
    
    response = requests.get(
        url,
        headers=HEADERS,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        params=params
    )
    
    if response.status_code == 200:
        issues = response.json()["issues"]
        return [{"key": issue["key"], 
                "summary": issue["fields"]["summary"],
                "status": issue["fields"]["status"]["name"]} 
               for issue in issues]
    else:
        print(f"❌ Failed to fetch stories for epic {epic_key}. Response: {response.text}")
        return None

def process_story(story_key):
    """Process a single story, generate release notes and get user approval."""
    print(f"\n📝 Processing story: {story_key}")
    
    issue_data = get_jira_description(story_key)
    if not issue_data:
        return False, False  # (approved, should_exit)
    
    print("\n🤖 Generating release notes using GPT-4...")
    release_notes = generate_release_notes(issue_data["description"])
    
    print("\n📋 Generated Release Notes:")
    print(f"------------------------\n{release_notes}\n------------------------")
    
    while True:
        choice = input("\nDo you want to approve these release notes? (Y)es/(N)o/(S)kip/(E)xit: ").upper()
        if choice in ['Y', 'N', 'S', 'E']:
            break
        print("Invalid input. Please enter Y, N, S, or E.")
    
    if choice == 'E':
        print("\n👋 Exiting script...")
        return False, True  # Signal to exit
    elif choice == 'Y':
        print(f"📤 Updating Jira field `{RELEASE_NOTES_FIELD}` with release notes...")
        update_jira_custom_field(story_key, RELEASE_NOTES_FIELD, release_notes)
        return True, False
    elif choice == 'N':
        print("❌ Release notes rejected. Moving to next story...")
        return False, False
    else:  # Skip
        print("⏭️ Skipping this story...")
        return False, False

def main():
    # Check if the user provided the issue key
    if len(sys.argv) < 2:
        print("Usage: python jira_bot.py <issue_key>")
        sys.exit(1)

    # Read command-line argument
    issue_key = sys.argv[1]

    print(f"📥 Fetching description for {issue_key}...")
    issue_data = get_jira_description(issue_key)
    
    if not issue_data:
        return
    
    # Check if the issue is an Epic or User Story
    issue_type = issue_data["issue_type"].lower()
    if issue_type not in ["epic", "story", "user story"]:
        print(f"⚠️ Warning: Issue type '{issue_data['issue_type']}' is neither an Epic nor a User Story")
        return
    
    print(f"📋 Issue Type: {issue_data['issue_type']}")
    
    # If it's an epic, process each non-closed story
    if issue_type == "epic":
        print("\n📎 Fetching non-closed stories for this epic...")
        stories = get_epic_stories(issue_key)
        if not stories:
            print("No non-closed stories found for this epic.\n")
            return
        
        print(f"\nFound {len(stories)} non-closed stories in this epic.")
        processed_count = 0
        approved_count = 0
        
        for story in stories:
            processed_count += 1
            print(f"\n[{processed_count}/{len(stories)}] Processing: {story['key']}: {story['summary']}")
            approved, should_exit = process_story(story['key'])
            if should_exit:
                print(f"\n✅ Exited early! Approved {approved_count} out of {processed_count} processed stories.")
                return
            if approved:
                approved_count += 1
        
        print(f"\n✅ Processing complete! Approved {approved_count} out of {len(stories)} stories.")
        return
    
    # For individual user story, process it directly
    approved, _ = process_story(issue_key)

# ✅ Run the Bot
if __name__ == "__main__":
    main()
