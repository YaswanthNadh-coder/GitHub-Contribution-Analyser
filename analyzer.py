import requests
import os
import sys
from collections import defaultdict
from datetime import datetime

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json",
}

# Added fields to the GraphQL query: createdAt, followers, following, totalCount for repos
QUERY = """
query UserStats($username: String!) {
  user(login: $username) {
    name
    login
    createdAt
    followers { totalCount }
    following { totalCount }
    repositories(
      first: 100
      ownerAffiliations: OWNER
      orderBy: { field: STARGAZERS, direction: DESC }
      isFork: false
    ) {
      totalCount
      nodes {
        name
        stargazerCount
        forkCount
        primaryLanguage { name color }
        languages(first: 10, orderBy: { field: SIZE, direction: DESC }) {
          edges {
            size
            node { name color }
          }
        }
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: 1) {
                totalCount
              }
            }
          }
        }
      }
    }
  }
}
"""

def fetch_github_stats(username: str) -> dict:
    if not GITHUB_TOKEN:
        raise ValueError(
            "GITHUB_TOKEN environment variable is not set. "
            "Please set it to your GitHub Personal Access Token."
        )
        
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": QUERY, "variables": {"username": username}},
        headers=HEADERS,
    )
    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"GraphQL errors: {data['errors']}")

    return data["data"]["user"]


def check_rate_limit() -> dict:
    if not GITHUB_TOKEN:
        return {"limit": "Unknown", "remaining": "Unknown", "resetAt": "N/A"}
        
    query = "{ rateLimit { limit remaining resetAt } }"
    res = requests.post(
        "https://api.github.com/graphql",
        json={"query": query}, 
        headers=HEADERS
    )
    res.raise_for_status()
    return res.json()["data"]["rateLimit"]


def compute_language_breakdown(repos: list) -> dict:
    lang_bytes = defaultdict(int)

    for repo in repos:
        if not repo.get("languages") or not repo["languages"].get("edges"):
            continue
        for edge in repo["languages"]["edges"]:
            lang = edge["node"]["name"]
            size = edge["size"]
            lang_bytes[lang] += size

    total = sum(lang_bytes.values())
    if total == 0:
        return {}

    return {
        lang: round((size / total) * 100, 2)
        for lang, size in sorted(lang_bytes.items(), key=lambda x: -x[1])
    }


def get_top_repos(repos: list, top_n: int = 5) -> list:
    return sorted(repos, key=lambda r: r["stargazerCount"], reverse=True)[:top_n]


def calculate_aggregates(repos: list) -> dict:
    total_stars = 0
    total_forks = 0
    total_commits = 0

    for repo in repos:
        total_stars += repo.get("stargazerCount", 0)
        total_forks += repo.get("forkCount", 0)
        
        branch_ref = repo.get("defaultBranchRef")
        if branch_ref and branch_ref.get("target") and branch_ref["target"].get("history"):
            total_commits += branch_ref["target"]["history"].get("totalCount", 0)

    return {
        "stars": total_stars,
        "forks": total_forks,
        "commits": total_commits
    }


if __name__ == "__main__":
    # Support passing the username via command line args
    username = sys.argv[1] if len(sys.argv) > 1 else "torvalds"
    
    try:
        # Check rate limits first
        rate_limit = check_rate_limit()
        # Parse the resetAt time only if it's a valid date
        if rate_limit['resetAt'] != "N/A":
            reset_time = datetime.strptime(rate_limit['resetAt'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
        else:
            reset_time = "N/A"
            
        print(f"API Rate Limit: {rate_limit['remaining']}/{rate_limit['limit']} (Resets at: {reset_time} UTC)")
        
        if rate_limit['remaining'] == 0:
            print("Rate limit exceeded! Please wait until it resets.")
            sys.exit(1)
            
        user = fetch_github_stats(username)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    repos = user.get("repositories", {}).get("nodes", [])
    total_repos_count = user.get("repositories", {}).get("totalCount", 0)
    
    # Parse date
    created_at = datetime.strptime(user['createdAt'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
    
    aggregates = calculate_aggregates(repos)

    print("=" * 60)
    print(f"👤 {user.get('name') or username} (@{user['login']})")
    print(f"📅 Joined:     {created_at}")
    print(f"👥 Followers:  {user['followers']['totalCount']:,} | Following: {user['following']['totalCount']:,}")
    print(f"📦 Repos:      {total_repos_count} public owned (Analyzed top {len(repos)} by stars)")
    print("-" * 60)
    print(f"⭐ Total Stars:   {aggregates['stars']:,}")
    print(f"🍴 Total Forks:   {aggregates['forks']:,}")
    print(f"💻 Total Commits: {aggregates['commits']:,} (on default branches)")
    print("=" * 60)

    print("\n⭐ Top Repositories:")
    for repo in get_top_repos(repos, 5):
        lang = repo.get("primaryLanguage")
        lang_name = lang["name"] if lang else "N/A"
        print(f"  {repo['name']:30s} ⭐ {repo['stargazerCount']:>6,}  🍴 {repo['forkCount']:>5,}  [{lang_name}]")

    print("\n📊 Language Breakdown (by bytes):")
    breakdown = compute_language_breakdown(repos)
    if breakdown:
        for lang, pct in list(breakdown.items())[:8]:
            bar = "█" * int(pct / 2)
            print(f"  {lang:20s} {bar:25s} {pct}%")
    else:
        print("  No language data available.")
    print("")
