# Dev Server

Start the local Pelican development server with autoreload.

## Instructions
1. Kill any existing Pelican or dev server processes:
   ```
   pkill -f "pelican content" 2>/dev/null
   pkill -f "python -m http.server" 2>/dev/null
   ```
2. Clean and start the dev server with autoreload:
   ```
   cd /Users/cranmer/Documents/GitHub/theoryandpractice-2026 && rm -rf output cache && pixi run -- pelican content -o output -s pelicanconf.py --autoreload --listen --port 8000
   ```
3. Run this command in the background so the conversation can continue
4. Confirm the server is running at http://localhost:8000
5. Note: pagefind (search indexing) is not run during autoreload — search won't work in dev mode. If the user needs search, run `pixi run -- npx pagefind --site output` separately.

## Options
- If the user says "stop" or "kill", just kill the processes without restarting
- If the user specifies a port, use that instead of 8000

## User input
$ARGUMENTS
