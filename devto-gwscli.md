---
title: "Install and Use the Google Workspace CLI: gwscli on Linux, From curl to Agent Skills"
published: false
description: "A step by step guide to the generally available Google Workspace CLI: one-line install, command discovery across nine Workspace services, incremental OAuth sign-in, JSON output, and the agent skill it ships for Claude Code and other agents."
tags: googleworkspace, cli, mcp, agents
cover_image: https://raw.githubusercontent.com/xbill9/gwscli/main/devto-cover.c0c85962.jpg
---

This article provides a step by step guide to installing and using the Google Workspace CLI, `gwscli`, on a Linux machine. Google made the CLI and the Workspace MCP servers generally available on November 24, 2026. The CLI gives a terminal, a script or an AI agent one command, `gwscli <service> <action>`, for Gmail, Drive, Docs, Sheets, Slides, Calendar, Chat, Tasks and People.

https://github.com/xbill9/gwscli

**One curl command installs a single static binary, and the CLI then describes itself: 69 actions across nine services, each with its own help text, required OAuth scopes and JSON output schema, all readable before you sign in.** Sign-in is incremental, so an agent can be granted read access to Drive recent files and nothing else.

---

#### What Is the Workspace CLI?

`gwscli` is a command-line client that reaches Google Workspace through the Workspace MCP services. Each command group maps to one MCP API, which fronts the regular Workspace API:

| Command group | MCP API | Underlying API |
| :--- | :--- | :--- |
| `gwscli gmail` | `gmailmcp.googleapis.com` | `gmail.googleapis.com` |
| `gwscli drive` | `drivemcp.googleapis.com` | `drive.googleapis.com` |
| `gwscli docs` | `docsmcp.googleapis.com` | `docs.googleapis.com` |
| `gwscli sheets` | `sheetsmcp.googleapis.com` | `sheets.googleapis.com` |
| `gwscli slides` | `slidesmcp.googleapis.com` | `slides.googleapis.com` |
| `gwscli calendar` | `calendarmcp.googleapis.com` | `calendar-json.googleapis.com` |
| `gwscli chat` | `chatmcp.googleapis.com` | `chat.googleapis.com` |
| `gwscli tasks` | `tasksmcp.googleapis.com` | `tasks.googleapis.com` |
| `gwscli people` | `people.googleapis.com` | `people.googleapis.com` |

The mapping comes from the README the installer drops in `~/.gwscli/README.md`. The action names match the tool names of the Workspace MCP servers, such as `drive list_recent_files` and `gmail search_threads`, so a workflow written against the CLI reads the same as one written against MCP.

---

#### At This Point You Should Have…

- A Linux or macOS machine with `bash` and `curl`, or Windows with PowerShell, on x86_64 or ARM64
- A Google Cloud project you can enable APIs in, and `gcloud` if you want to enable them from the terminal
- A browser on the same machine as the terminal, for the one-time sign-in

---

#### Step 1 — Read the Installer, Then Run It

The documented install is a pipe into bash. The script is short, so download it first and read it:

```shell
mkdir -p ~/dl && cd ~/dl
curl -fsSL https://dl.google.com/workspace-cli/install.sh -o install.sh
wc -l install.sh
```

```text
97 install.sh
```

It detects the platform (`linux`, `linux_arm64`, `macos_silicon`, `macos_intel`), downloads the binary from `dl.google.com/workspace-cli/<platform>/gwscli` into a temporary file inside the install directory, runs `gwscli version` on it, and only then moves it into place. On macOS it also clears the quarantine attribute. It writes nothing outside `~/.local/bin` and `~/.gwscli`.

```shell
bash install.sh
```

```text
Downloading gwscli (linux)...
Installed gwscli to /home/xbill/.local/bin/gwscli
Next: read /home/xbill/.gwscli/README.md to set up authentication.
```

If `~/.local/bin` is not on your `PATH`, the script prints the `export` line to add. Set `GWSCLI_INSTALL_DIR` before running it to install somewhere else.

On Windows the same job is one PowerShell line:

```powershell
iex ((New-Object Net.WebClient).DownloadString('https://dl.google.com/workspace-cli/install.ps1'))
```

---

#### Step 2 — Check the Binary

```shell
gwscli version
file ~/.local/bin/gwscli
ls ~/.gwscli
```

```text
gwscli version 1.0.6.1026726559
/home/xbill/.local/bin/gwscli: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, stripped
NOTICES.txt  README.md
```

The binary is 11,673,751 bytes and statically linked, so there is no runtime, package manager or virtual environment to set up. It does not update itself: re-run the installer to get a new version.

---

#### Step 3 — Discover the Services

```shell
gwscli --help
```

```text
Available Services:
  calendar    Schedule meetings, check availability, and manage events
  chat        Send messages, read conversations, and manage Chat spaces
  docs        Read and edit Google Docs documents
  drive       Search, upload, download, and organize Drive files
  gmail       Search emails, read threads, manage labels, and create drafts
  people      Search directory profiles and view personal contacts
  sheets      Read, write, format, and analyze Sheets data
  slides      Read and edit Slides presentations
  tasks       Create, read, and manage Google Tasks and task lists

Utility Commands:
  auth        Sign in, sign out, and manage authentication
  logging     Manage telemetry and usage logging
  privacy     Print the Privacy Policy URL
  skills      Discover and manage agent skills
  terms       Print the Terms of Service URL
  version     Print the version
```

`gwscli <service> --help` lists each service's actions. Counted from that output for every service on version 1.0.6:

| Service | Actions | Examples |
| :--- | ---: | :--- |
| gmail | 23 | `search_threads`, `get_thread`, `create_draft`, `label_thread`, `trash_message` |
| calendar | 9 | `list_events`, `search_events`, `suggest_time`, `create_event` |
| drive | 9 | `search_files`, `list_recent_files`, `read_file_content`, `create_file` |
| tasks | 9 | `list_tasks`, `create_task`, `complete_task`, `undelete_task` |
| sheets | 6 | `get_values`, `update_values`, `update_formulas` |
| chat | 4 | `search_conversations`, `list_messages`, `search_messages`, `send_message` |
| slides | 4 | `read_presentation`, `read_slide_page_thumbnail`, `update_presentation` |
| people | 3 | `get_user_profile`, `search_contacts`, `search_directory_people` |
| docs | 2 | `read_doc`, `update_doc` |
| **Total** | **69** | |

Gmail has a create-draft action and no send action, so mail written by an agent waits in Drafts for a person to send it.

---

#### Step 4 — Read an Action Before Running It

Every action has three views that work with no sign-in at all.

`--help` gives the description, the flags and the output format:

```shell
gwscli drive list_recent_files --help
```

```text
The default page size is 10. Utilize `nextPageToken` to paginate through the results.

Usage:
  gwscli drive list_recent_files [flags]

Flags:
      --excludeContentSnippets    If 'true', the content snippet will be excluded from the response. ...
      --includeExternalityState   Optional. When true, also returns 'externality_state' for each file. Defaults to 'false'.
      --orderBy string            The sort order for the files.
      --pageSize int              The maximum number of files to return.
      --pageToken string          The page token to use for pagination.
      --snippetVerbosity string   Optional. Set to specify how verbose the snippets should be. ...
      --schema                    Print the output schema and structure, then exit.
      --show-scopes               Show the OAuth scopes required for this command in the help output.

Output Format:
  Format: JSON
  Run with --schema to view full response structure and field definitions.
```

`--show-scopes` adds the OAuth scopes the action can use, and the smallest set it needs:

```shell
gwscli drive list_recent_files --help --show-scopes
```

```text
OAuth Scopes:
  All Supported Scopes:
    - https://www.googleapis.com/auth/drive
    - https://www.googleapis.com/auth/drive.appdata
    - https://www.googleapis.com/auth/drive.file
    - https://www.googleapis.com/auth/drive.meet.readonly
    - https://www.googleapis.com/auth/drive.metadata
    - https://www.googleapis.com/auth/drive.metadata.readonly
    - https://www.googleapis.com/auth/drive.photos.readonly
    - https://www.googleapis.com/auth/drive.readonly

  Recommended Minimal Scopes:
    - https://www.googleapis.com/auth/drive.file
    - https://www.googleapis.com/auth/drive.metadata.readonly
    - https://www.googleapis.com/auth/drive.readonly
```

`--schema` prints the JSON Schema of the response and exits without calling Google:

```shell
gwscli drive list_recent_files --schema | head -5
```

```text
{
  "$defs": {
    "CalendarSource": {
      "description": "Represents a Google Calendar event linked from Drive, such as a Drive Project source.",
      "properties": {},
```

The README says the action-level `--help` queries the backend for current parameter details, so the help text tracks the MCP server's tool definitions.

---

#### Step 5 — Install the Agent Skill

The CLI ships its own agent skill: a `SKILL.md` that teaches an agent the sign-in rules, the headless safety rules and the command layout.

```shell
gwscli skills list
gwscli skills install --dir ./skills
wc -l skills/gwscli/SKILL.md
```

```text
gwscli
Installing skills to ./skills...
318 skills/gwscli/SKILL.md
```

Point `--dir` at your agent's skills directory: `~/.claude/skills` for Claude Code, or `~/.agents/skills`, the README's example for other agents. Restart the agent after installing. To update later, `--overwrite` replaces the installed copy; installing to a temporary directory and running `diff -ru` first shows what changes.

---

#### Step 6 — Create an OAuth Client

`gwscli` signs in with an OAuth client from your own Google Cloud project. Until one exists, every data command stops with a clear message:

```shell
gwscli auth status
gwscli drive list_recent_files
```

```text
No logged in user found.
Error: failed to obtain token source: no valid cached token found. Run `gwscli auth login drive list_recent_files` before rerunning this command
```

The fastest route is the Cloud console's personal-mode shortcut, linked from the README:

```text
https://console.cloud.google.com/auth/overview/personal?apis=ws,wsmcp,tasksmcp&clientType=desktop&isAgent=true
```

It creates or selects a project, enables the Workspace and MCP APIs, and pre-selects **Desktop app** and **Use this client for an AI-powered agent**. Download the client JSON.

For an existing project, enable the APIs yourself:

```shell
gcloud services enable --project=PROJECT_ID \
    gmail.googleapis.com drive.googleapis.com docs.googleapis.com \
    sheets.googleapis.com slides.googleapis.com calendar-json.googleapis.com \
    chat.googleapis.com people.googleapis.com tasks.googleapis.com

gcloud services enable --project=PROJECT_ID \
    gmailmcp.googleapis.com drivemcp.googleapis.com docsmcp.googleapis.com \
    sheetsmcp.googleapis.com slidesmcp.googleapis.com \
    calendarmcp.googleapis.com chatmcp.googleapis.com \
    tasksmcp.googleapis.com
```

Then create the client in the console with these three settings:

- **Application type: Desktop app.** The CLI listens on a random local port for the OAuth callback, and only the Desktop type allows that.
- **Use this client for an AI-powered agent: checked.** This marks the client as an agent client, which Google's November 24 announcement makes the way agents identify themselves.
- **Test users:** with an External consent screen, add your own address or consent is refused.

---

#### Step 7 — Register the Client and Sign In

```shell
gwscli auth setup --oauth_client_file=$HOME/Downloads/client_secret.json
```

`auth setup` signs you out before saving and asks for a `Y` on stdin, so it replaces any tokens granted earlier.

Sign-in takes the commands or services you want to allow, and requests only their scopes:

```shell
gwscli auth login drive list_recent_files                 # one action
gwscli auth login "chat search_messages" "gmail search_threads"   # several actions
gwscli auth login gmail                                   # a whole service
gwscli auth login chat --bundle=readonly                  # read-only scopes for a service
gwscli auth login                                         # everything
```

Each prints a URL. Open it in the browser on the same machine, approve, and the CLI caches the token. `gwscli auth status` lists the granted scopes and `gwscli auth refresh` renews the token.

A read-only sign-in across six services:

```shell
gwscli auth login --bundle=readonly drive calendar gmail docs sheets tasks
gwscli auth status
```

```text
Granted the following scopes:
  - https://www.googleapis.com/auth/calendar.events.readonly
  - https://www.googleapis.com/auth/calendar.readonly
  - https://www.googleapis.com/auth/documents.readonly
  - https://www.googleapis.com/auth/drive.metadata.readonly
  - https://www.googleapis.com/auth/drive.readonly
  - https://www.googleapis.com/auth/gmail.labels.readonly
  - https://www.googleapis.com/auth/gmail.messages.readonly
  - https://www.googleapis.com/auth/gmail.readonly
  - https://www.googleapis.com/auth/spreadsheets.readonly
  - https://www.googleapis.com/auth/tasks.readonly
```

---

#### 🔎 Tip: The Read-Only Bundle Leaves Out `drive.file`

The CLI checks a command's **Recommended Minimal Scopes** before calling Google, and both `drive list_recent_files` and `drive search_files` list `drive.file` there. `--bundle=readonly` grants `drive.readonly` and `drive.metadata.readonly` only, so both commands stop:

```shell
gwscli drive list_recent_files --pageSize 5 --excludeContentSnippets
```

```text
Error: failed to obtain token source: no valid cached token found. Run `gwscli auth login drive list_recent_files` before rerunning this command
```

Sign in per action for Drive. Logins add to the cached grant, so the earlier scopes stay:

```shell
gwscli auth login "drive list_recent_files" "drive search_files"
```

`drive.file` covers only files the app creates or opens, so the grant stays narrow.

---

#### Step 8 — Run Commands and Parse the Output

Lists and records come back as JSON on stdout, so they pipe into `jq`. This example is from the README:

```shell
gwscli drive search_files --query="title contains 'Report'" | jq '.files[] | {title: .title, id: .id}'
```

Document content, such as `docs read_doc`, comes back as Markdown text, which goes to a file or a pager. Utility commands print plain text.

A typical read-only agent session needs four sign-ins and no write scopes:

```shell
gwscli auth login "drive list_recent_files" "drive read_file_content" \
  "calendar list_events" "gmail search_threads"
gwscli drive list_recent_files --pageSize 5 --excludeContentSnippets
gwscli calendar list_events
```

---

#### 🔎 Tip: Day One Still Asks for the Developer Preview

On November 24, 2026, with a personal-mode project, every MCP API enabled and the scopes granted, Calendar, Gmail and Tasks answered:

```text
Access to this tool requires that your Google Cloud project (<project-number>) is enrolled in the Google Workspace Developer Preview Program. Please see https://developers.google.com/workspace/preview
```

Drive, with `drive.file` added, answered:

```text
The caller does not have permission
```

The announcement gives the rollout as two weeks. Until it reaches your project, enroll it in the Developer Preview Program, and on a Workspace account check that an admin allows agent clients under **Security > API Controls**. The CLI side, from install to granted scopes, works today.

---

#### Step 9 — Bring Your Own Token

When something else already manages tokens, such as a CI job or a service that does its own OAuth, skip `setup` and `login` and pass the token on each call:

```shell
gwscli --oauth_token="$ACCESS_TOKEN" calendar list_events
```

The token must already carry the action's scopes, which `--show-scopes` lists. The CLI does not refresh it in this mode. A token on the command line also lands in shell history and the process list, so read it from a variable that a secret store fills.

---

#### 🔎 Tip: Sign In Where the Browser Is

`gwscli auth login` waits for a redirect to `http://127.0.0.1:<port>/`. On a headless VM, in Cloud Shell or over SSH, that redirect never reaches the CLI. Run the login on your own machine, or forward the port the command prints:

```shell
ssh -L <port>:127.0.0.1:<port> user@host
```

The README tells agents the same thing: `auth login` and `auth setup` are interactive and hang in a script, so an agent that hits an auth error should stop and ask its user to sign in.

---

#### 🔎 Tip: Telemetry Is On by Default

```shell
gwscli logging status
```

```text
Telemetry logging is enabled.
```

`gwscli logging off` turns it off. `gwscli privacy` and `gwscli terms` print the policy URLs.

---

#### 🔎 Tip: Treat Workspace Content as Untrusted Input

The README opens with a prompt-injection warning. An agent that reads mail or documents from outside your organisation can meet hidden instructions in them, and with write scopes it can act on them. Grant the narrowest sign-in the task needs, prefer `--bundle=readonly`, and review what the agent does.

---

#### What Do the New Usage Tiers Mean for the CLI?

The November 24, 2026 Workspace Updates post puts the CLI and the MCP servers under the same usage tiers as the Workspace APIs, starting with Gmail, Drive and Calendar:

| Tier | Cost | Who it is for |
| :--- | :--- | :--- |
| Standard | no charge, published rate limits | the post says over 99% of active developers fit here |
| Scaled | billed from April 1, 2027 for use above daily free allowances | projects that need higher quota |

Two dates matter for anything built on Workspace:

- **February 1, 2027:** AI agents must reach Workspace data through MCP, and technical enforcement starts. The CLI already goes through the MCP services.
- **April 1, 2027:** Scaled tier billing begins. A project over Standard limits that takes no action may be throttled.

Admins control agent access in the Admin console under **Security > API Controls**. The post gives no numeric quotas; they are published separately.

---

#### Compare and Contrast: The Two Ways to Authenticate

| | Own OAuth client (`auth setup` + `auth login`) | Own token (`--oauth_token`) |
| :--- | :--- | :--- |
| One-time setup | Desktop client JSON, browser consent | none in the CLI |
| Scope control | per action, per service, or `--bundle=readonly` | whatever the token holds |
| Token refresh | handled by the CLI (`auth refresh`) | yours |
| Works headless | after a login on a machine with a browser | 🥇 yes |
| Token exposure | cached by the CLI | on the command line unless read from a variable |
| Best for | 🥇 a person or a local agent | CI and services with their own OAuth |

---

#### So, Which One?

For a developer laptop or a local agent such as Claude Code, use your own OAuth client and sign in per action. The consent screen then lists exactly what the agent can touch, and `gwscli auth logout` revokes it. Use `--oauth_token` when another system already owns the token lifecycle.

---

#### Cleaning Up

```shell
gwscli auth logout     # revoke the cached token and delete it
gwscli auth reset      # also forget the registered OAuth client
rm ~/.local/bin/gwscli && rm -r ~/.gwscli
```

Granted access is also listed at myaccount.google.com/connections, and the OAuth client can be deleted from the Credentials page of the Cloud project.

---

#### Summary

The goal of this article was to install the Google Workspace CLI and show how to use it from a terminal and from an agent. The key to the solution was the CLI's own discovery: `--help`, `--show-scopes` and `--schema` describe every action before any sign-in, and sign-in then grants only the scopes those actions need. The results were:

- 🟢 Install is one `curl` and `bash`, and produces a single static binary of 11,673,751 bytes (11.7 MB) on Linux x86_64. The script is 97 lines and readable before running.
- 🟢 Version 1.0.6 exposes 69 actions across nine services, plus `auth`, `skills`, `logging`, `privacy`, `terms` and `version`.
- 🟢 Help, scopes and response schemas all work with no account signed in.
- 🟢 `gwscli skills install` adds a ready-made agent skill for Claude Code or any agent that reads `SKILL.md` files.
- ⚠️ Sign-in needs a Desktop OAuth client marked for AI agents and a browser on the same machine; over SSH, forward the callback port.
- ⚠️ `--bundle=readonly` omits `drive.file`, which Drive's list and search commands require; sign in per action for Drive.
- ❌ On launch day, Calendar, Gmail and Tasks asked for Developer Preview enrollment and Drive returned a permission error, with every API enabled and every scope granted.
- ⚠️ Telemetry is on until `gwscli logging off`.
- ❌ No auto-update; re-run the installer for new versions.

Scope: one Linux x86_64 machine, `gwscli` version 1.0.6.1026726559, one personal-mode Google Cloud project, run on November 24, 2026, the day of the announcement. Install, help, scopes, schema, skills, logging, `auth setup`, both sign-ins and the error responses were run and their output is shown above. No data command returned Workspace content on that day, so the `jq` example and the session in Step 8 come from the README and help text, as does the token mode in Step 9. Usage-tier facts are from Google's Workspace Updates post of the same date.

The strategy for using the Google Workspace CLI was validated with an incremental step by step approach.

---

#### References

- Google Workspace CLI guide: https://developers.google.com/workspace/guides/workspace-cli
- Workspace Updates, MCP servers, CLI and usage tiers: https://workspaceupdates.googleblog.com/2026/11/mcp-servers-cli-standardized-usage-tiers-now-available.html
- Create OAuth client credentials: https://developers.google.com/workspace/guides/create-credentials
- Repository for this article: https://github.com/xbill9/gwscli
