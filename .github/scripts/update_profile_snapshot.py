import json
import os
import urllib.request
from pathlib import Path

USERNAME = "RajenderMohanVerma"
OUTPUT = Path("assets/profile-snapshot.svg")


def fetch_public_repo_count():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "RajenderMohanVerma-profile-snapshot",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Try fast user endpoint first (official public_repos count)
    user_url = f"https://api.github.com/users/{USERNAME}"
    try:
        request = urllib.request.Request(user_url, headers=headers)
        with urllib.request.urlopen(request, timeout=15) as response:
            user_data = json.load(response)
            if "public_repos" in user_data:
                count = int(user_data["public_repos"])
                print(f"Fetched public_repos count directly from user profile: {count}")
                return count
    except Exception as e:
        print(f"Direct user profile fetch fallback: {e}")

    # Fallback to paginated repository listing
    count = 0
    page = 1
    while True:
        url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&type=owner"
        request = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(request, timeout=20) as response:
            repos = json.load(response)

        if not repos:
            break

        count += sum(1 for repo in repos if not repo.get("private", False))

        if len(repos) < 100:
            break

        page += 1

    return count


def build_svg(repo_count):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="380" viewBox="0 0 1100 380" role="img" aria-labelledby="title desc">
  <title id="title">Rajender Mohan Verma GitHub Profile Snapshot</title>
  <desc id="desc">Professional GitHub profile snapshot with a live repository count and current technology focus.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#07111F"/>
      <stop offset=".52" stop-color="#111B35"/>
      <stop offset="1" stop-color="#241343"/>
    </linearGradient>
    <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#22D3EE"/>
      <stop offset=".55" stop-color="#6366F1"/>
      <stop offset="1" stop-color="#C084FC"/>
    </linearGradient>
  </defs>
  <rect width="1100" height="380" rx="24" fill="url(#bg)"/>
  <rect x="1" y="1" width="1098" height="378" rx="23" fill="none" stroke="#334155" stroke-width="2"/>
  <circle cx="1040" cy="40" r="150" fill="#6366F1" opacity=".09"/>
  <circle cx="40" cy="350" r="140" fill="#22D3EE" opacity=".06"/>

  <rect x="24" y="24" width="650" height="128" rx="20" fill="#0B1627" stroke="url(#line)" stroke-width="2"/>
  <circle cx="72" cy="88" r="31" fill="#07111F" stroke="#22D3EE" stroke-width="2"/>
  <text x="72" y="99" text-anchor="middle" fill="#22D3EE" font-family="Arial,sans-serif" font-size="26" font-weight="800">R</text>
  <text x="122" y="66" fill="#FFFFFF" font-family="Arial,sans-serif" font-size="25" font-weight="800">Rajender Mohan Verma</text>
  <text x="122" y="92" fill="#22D3EE" font-family="Arial,sans-serif" font-size="14" font-weight="700">@RajenderMohanVerma</text>
  <text x="122" y="119" fill="#94A3B8" font-family="Arial,sans-serif" font-size="13">Full-Stack Developer • Python Developer • MCA Student</text>

  <rect x="692" y="24" width="184" height="128" rx="20" fill="#0B1627" stroke="#334155"/>
  <text x="784" y="82" text-anchor="middle" fill="#FFFFFF" font-family="Arial,sans-serif" font-size="34" font-weight="800">{repo_count}</text>
  <text x="784" y="108" text-anchor="middle" fill="#7890B4" font-family="Arial,sans-serif" font-size="12" font-weight="700" letter-spacing="1">REPOSITORIES</text>
  <text x="784" y="129" text-anchor="middle" fill="#64748B" font-family="Arial,sans-serif" font-size="10">Live GitHub count</text>

  <rect x="894" y="24" width="182" height="128" rx="20" fill="#0B1627" stroke="#334155"/>
  <text x="985" y="82" text-anchor="middle" fill="#FFFFFF" font-family="Arial,sans-serif" font-size="28" font-weight="800">MCA</text>
  <text x="985" y="108" text-anchor="middle" fill="#A5B4FC" font-family="Arial,sans-serif" font-size="12" font-weight="700" letter-spacing="1">CURRENTLY PURSUING</text>
  <text x="985" y="129" text-anchor="middle" fill="#64748B" font-family="Arial,sans-serif" font-size="10">JIMS, Rohini</text>

  <rect x="24" y="170" width="1052" height="154" rx="20" fill="#0B1627" stroke="#334155"/>
  <text x="48" y="202" fill="#FFFFFF" font-family="Arial,sans-serif" font-size="16" font-weight="800">Top Languages &amp; Core Stack</text>
  <text x="48" y="224" fill="#64748B" font-family="Arial,sans-serif" font-size="11">Technology focus from the current profile</text>

  <rect x="48" y="242" width="1004" height="13" rx="6" fill="#172338"/>
  <rect x="48" y="242" width="240" height="13" rx="6" fill="#3776AB"/>
  <rect x="288" y="242" width="210" height="13" fill="#F7DF1E"/>
  <rect x="498" y="242" width="195" height="13" fill="#3776AB" opacity=".82"/>
  <rect x="693" y="242" width="180" height="13" fill="#A8B9CC"/>
  <rect x="873" y="242" width="179" height="13" rx="6" fill="#4F46E5"/>

  <circle cx="54" cy="282" r="5" fill="#3776AB"/><text x="68" y="286" fill="#E2E8F0" font-family="Arial,sans-serif" font-size="12" font-weight="700">Python</text>
  <circle cx="184" cy="282" r="5" fill="#F7DF1E"/><text x="198" y="286" fill="#E2E8F0" font-family="Arial,sans-serif" font-size="12" font-weight="700">JavaScript</text>
  <circle cx="324" cy="282" r="5" fill="#3776AB"/><text x="338" y="286" fill="#E2E8F0" font-family="Arial,sans-serif" font-size="12" font-weight="700">Java</text>
  <circle cx="426" cy="282" r="5" fill="#A8B9CC"/><text x="440" y="286" fill="#E2E8F0" font-family="Arial,sans-serif" font-size="12" font-weight="700">C++</text>
  <circle cx="525" cy="282" r="5" fill="#4F46E5"/><text x="539" y="286" fill="#E2E8F0" font-family="Arial,sans-serif" font-size="12" font-weight="700">SQL</text>
  <text x="48" y="307" fill="#64748B" font-family="Arial,sans-serif" font-size="10">Web: HTML • CSS • React • Flask • Django • Node.js • Bootstrap</text>

  <rect x="24" y="340" width="1052" height="2" rx="1" fill="url(#line)" opacity=".8"/>
  <text x="24" y="362" fill="#22D3EE" font-family="Arial,sans-serif" font-size="11" font-weight="700">BUILD • LEARN • DEPLOY</text>
  <text x="1076" y="362" text-anchor="end" fill="#64748B" font-family="Arial,sans-serif" font-size="10">{repo_count} public repositories • Live count</text>
</svg>
'''


if __name__ == "__main__":
    count = fetch_public_repo_count()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_svg(count), encoding="utf-8")
    print(f"Updated profile snapshot: {count} public repositories")
