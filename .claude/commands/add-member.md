# Add Group Member

Add a new person to the collaborators/group members page.

## Input
The user will provide details in natural language, possibly including a personal website URL. Fetch the URL if provided to extract photo, links, and other info.

## Categories
- `students` — PhD students and undergraduate researchers
- `postdocs` — Postdoctoral researchers
- `scientists` — Research scientists and staff
- `collaborators` — Frequent research collaborators

## Required fields
- `name` (full name)
- `category` (one of the IDs above)
- `current` (true/false — is this person currently in the group?)

## Optional fields
- `role` (e.g., "PhD Student", "Postdoc", "Research Scientist")
- `affiliation` (e.g., "University of Wisconsin-Madison")
- `start_year` (year they joined)
- `end_year` (year they left, if not current)
- `photo` (URL to headshot)
- `links` (nested object with any of):
  ```yaml
  links:
    website: "https://example.com"
    github: "username"
    twitter: "username"
    bluesky: "handle"
    linkedin: "username"
    scholar: "GOOGLE_SCHOLAR_ID"
    inspire: "INSPIRE_ID"
  ```

## File to edit
`content/collaborators.yml`

## Format
Entries go under `people:`, grouped by category. Follow this YAML format:

```yaml
  - name: "First Last"
    category: students
    current: true
    role: "PhD Student"
    affiliation: "University of Wisconsin-Madison"
    start_year: 2024
    photo: "https://example.com/photo.jpg"
    links:
      website: "https://example.com"
      github: "username"
```

## Instructions
1. Read `content/collaborators.yml` to see existing entries and find the right section
2. If a website URL is provided, fetch it to extract photo, role, and social links
3. Insert the new entry in the appropriate category section
4. For current members, set `current: true`; for alumni, set `current: false` and include `end_year`
5. After editing, rebuild the site with `pixi run pelican content -s pelicanconf.py`

## User input
$ARGUMENTS
