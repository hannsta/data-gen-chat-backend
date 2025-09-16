## User Instructions

### Overview
Follow these steps to create your Lovable app, ensure Pendo is set up with good tags, generate your app README, and interact with the data-generation bot.

### Step 1 — Build your app in Lovable
- **Create your app** in Lovable and build out the core flows you want to simulate.
- **Publish the app** and note the live URL (e.g., `https://your-app.lovable.app`). You will provide this to the bot and backend later.

### Step 2 — Configure Pendo in your Lovable app (with good tags)
- **Install and initialize the Pendo agent** in your app so page loads and interactions are tracked.
- **Provide stable Visitor and Account IDs** so simulated sessions map to consistent users/accounts.
- **Tag key pages and UI elements** you want the simulation to traverse. Favor selectors that are stable and semantic.
- Use the copy/paste prompt in `lovable-pendo-instructions.md` to help Lovable configure Pendo and produce solid tagging guidance.

### Step 3 — Generate your app README in Lovable
- Ask Lovable to generate a README for your app using the copy/paste prompt in `lovable-readme-instructions.md`.
- Save the generated README in your app repo for reference (optional but recommended).


### Step 4 — Interact with the bot
- The bot orchestrates workflow simulation against your Lovable app.
- See guidance and constraints in `prompts/agent-instructions.md`.
- Provide the bot with:
  - **Your live Lovable app URL** (from Step 1)
  - **Confirmation that Pendo is installed** and **which elements/pages are tagged** (from Step 2)
  - Any specific user journeys you want covered
- The bot will produce a workflow definition and can call the backend to validate or execute simulations.

### B2B Account Structure (Advanced)
For **B2B SaaS platforms** where multiple users work for the same company:
- **Define company accounts** with attributes (tier, industry, team size, region, revenue, etc.)
- **Create user segments** representing different roles (admin, manager, contributor) 
- **Mixed user types per company**: Same company can have admins, power users, and basic users
- **Rich Pendo reporting**: Analyze usage by account (company) AND by user segment
- **Example**: "TechCorp" account has 12 users: 2 admins, 7 managers, 3 contributors

**🎯 Rich Metadata Passed to Pendo:**
- **All account and user attributes** from your JSON are automatically included in Pendo events

The bot will automatically detect B2B scenarios and suggest account-based structures when appropriate.

### Fast validation vs full execution
- The backend supports a fast validation mode to quickly check selectors and paths.
- In your requests (via the bot or API), set `test_mode: true` for quick validation; use `false` for full execution.

### Helpful references
- **Agent instructions**: `prompts/agent-instructions.md`
- **Pendo setup & tagging prompt**: `prompts/lovable-pendo-instructions.md`
- **App README generation prompt**: `prompts/lovable-readme-instructions.md`
- **Simulation reference**: `prompts/simulation_reference.md`
- **Example workflows**: `workflows/`

### Troubleshooting
- If Playwright complains about missing browsers, run: `playwright install chromium`.
- Check API logs in your terminal; API docs at `/docs` list the `POST /execute_workflow` endpoint.
- For quicker iteration, use validation mode (`test_mode: true`) before running large user counts. 