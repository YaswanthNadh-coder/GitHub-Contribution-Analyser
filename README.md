# GitHub Contribution Analyser

A lightweight command-line tool written in Python that utilizes the GitHub GraphQL API to fetch, analyze, and beautifully display a user's GitHub repository statistics.

## Features

- **Web Interface:** A stunning, interactive dashboard built with Vanilla JS and Chart.js to visualize statistics with donuts and bar charts.
- **Profile Overview:** View account creation date, followers, following, and total public owned repositories.
- **Aggregate Statistics:** Computes total stars, forks, and commits (across default branches) for up to 100 top repositories.
- **Top Repositories:** Displays the top 5 repositories sorted by stargazer count.
- **Language Breakdown:** Calculates the exact language usage percentage across the user's repositories (by bytes) and renders a visual bar chart right in your terminal.
- **Rate Limit Checker:** Automatically checks and displays your GraphQL API rate limits before fetching data.

## Prerequisites

- Python 3.7+
- `requests` library

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YaswanthNadh-coder/GitHub-Contribution-Analyser.git
   cd GitHub-Contribution-Analyser
   ```

2. **Install dependencies:**
   ```bash
   pip install requests
   ```

3. **Get a GitHub Personal Access Token:**
   - Go to [GitHub Developer Settings](https://github.com/settings/tokens)
   - Click **Generate new token (classic)**
   - Give it a descriptive name and ensure it has basic `read` permissions.

4. **Set the Environment Variable:**
   Set the generated token as an environment variable in your terminal.

   **Windows (PowerShell):**
   ```powershell
   $env:GITHUB_TOKEN="your_personal_access_token_here"
   ```

   **Mac / Linux / Git Bash:**
   ```bash
   export GITHUB_TOKEN="your_personal_access_token_here"
   ```

## Usage

Run the script by passing the targeted GitHub username as an argument:

```bash
python analyzer.py <github_username>
```

If no username is provided, it will default to `torvalds`.

## Web UI Usage

The project now includes a beautiful web dashboard. To use it:

1. Locate the `index.html` file in the project directory.
2. Open it directly in any modern web browser (Chrome, Firefox, Edge, etc.).
3. Enter the Target GitHub Username and your Personal Access Token in the search box.
4. Click **Analyze** to generate the interactive charts and report.

### Example Output

```text
API Rate Limit: 4987/5000 (Resets at: 2026-04-17 09:46:03 UTC)
============================================================
👤 Guthikonda Yaswanth Nadh (@YaswanthNadh-coder)
📅 Joined:     2025-07-23
👥 Followers:  1 | Following: 3
📦 Repos:      5 public owned (Analyzed top 5 by stars)
------------------------------------------------------------
⭐ Total Stars:   5
🍴 Total Forks:   0
💻 Total Commits: 38 (on default branches)
============================================================

⭐ Top Repositories:
  Pixel-Cipher                   ⭐      2  🍴     0  [Python]
  Pixel-Assasins                 ⭐      2  🍴     0  [HTML]
  todoapp                        ⭐      1  🍴     0  [TypeScript]
  GitHub-Contribution-Analyser   ⭐      0  🍴     0  [Python]
  Nexus-Exchange                 ⭐      0  🍴     0  [JavaScript]

📊 Language Breakdown (by bytes):
  TypeScript           ██████████████████        36.55%
  JavaScript           ███████████████           31.69%
  Python               ██████                    13.08%
  CSS                  █████                     10.3%
  HTML                 ██                        5.87%
  PLpgSQL              █                         2.51%
```