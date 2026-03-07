# Add Talk

Add a new presentation/talk entry to the website.

## Input
The user will provide details in natural language, possibly including a URL to an event page. Extract whatever information is available. If a URL is provided, fetch it to get missing details.

## Required fields
- `date` (YYYY-MM-DD)
- `meeting` (event/series name)

## Optional fields
- `title` (use TBD if unknown)
- `meetingurl` (link to event page)
- `location` (venue and/or city)
- `video` (YouTube or other video link)
- `focus-area` (e.g., `as`, `ia` — only if relevant to IRIS-HEP)

## File to edit
`content/presentations.yml`

## Format
Entries go under the `presentations:` list, appended in chronological order at the end. Follow this YAML format:

```yaml
  - title: "Talk Title Here"
    meeting: Event or Series Name
    meetingurl: https://example.com/event
    location: Venue, City
    date: YYYY-MM-DD
    video: https://youtube.com/watch?v=xxx
```

## Instructions
1. Read the end of `content/presentations.yml` to see the latest entries
2. If a URL is provided, fetch it to extract title, date, location, and other metadata
3. Insert the new entry in chronological order (typically at the end)
4. Use `TBD` for the title if not yet known
5. After editing, rebuild the site with `pixi run pelican content -s pelicanconf.py`

## User input
$ARGUMENTS
