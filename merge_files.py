"""Merge Stitch design HTML with boilerplate script blocks."""
import re
import subprocess

PROJECT = r"C:\Users\DELL\.gemini\antigravity\scratch\lumiere-auctions"
STITCH = r"C:\Users\DELL\OneDrive\Desktop\stitch_elysian_luxury_auction_platform"

MERGES = [
    {
        "stitch": f"{STITCH}\\auction_detail_elysian_auctions\\code.html",
        "boilerplate": f"{PROJECT}\\frontend\\auction-detail.html",
        "output": f"{PROJECT}\\frontend\\auction-detail.html",
    },
    {
        "stitch": f"{STITCH}\\sign_in_elysian_auctions\\code.html",
        "boilerplate": f"{PROJECT}\\frontend\\login.html",
        "output": f"{PROJECT}\\frontend\\login.html",
    },
    {
        "stitch": f"{STITCH}\\user_dashboard_elysian_auctions\\code.html",
        "boilerplate": f"{PROJECT}\\frontend\\dashboard.html",
        "output": f"{PROJECT}\\frontend\\dashboard.html",
    },
]

# Step 1: Restore boilerplate files from git (they were corrupted by previous run)
print("Restoring boilerplate files from git...")
subprocess.run(
    ["git", "checkout", "--", "frontend/auction-detail.html", "frontend/login.html", "frontend/dashboard.html"],
    cwd=PROJECT, check=True
)
print("Restored.\n")

# Step 2: Read all boilerplate files BEFORE overwriting
boilerplate_contents = {}
for m in MERGES:
    with open(m["boilerplate"], "r", encoding="utf-8") as f:
        boilerplate_contents[m["output"]] = f.read()

# Step 3: Process each merge
for m in MERGES:
    print(f"=== Processing: {m['output']} ===")

    with open(m["stitch"], "r", encoding="utf-8") as f:
        stitch = f.read()

    bp = boilerplate_contents[m["output"]]

    # Extract all <script>...</script> blocks from boilerplate that are NOT:
    # - External scripts (have src= attribute)
    # - Tailwind config (have id="tailwind-config")
    pattern = r'<script(?![^>]*\bsrc\b)(?![^>]*\bid="tailwind-config")(?:[^>]*)>.*?</script>'
    scripts = re.findall(pattern, bp, re.DOTALL)

    print(f"  Found {len(scripts)} script block(s) in boilerplate")

    if not scripts:
        print("  WARNING: No script blocks found! Skipping.")
        continue

    # Remove Stitch's own trailing <script> blocks (the ones just before </body>)
    # Find the last </footer> or </main> and remove everything between that and </body>
    # Strategy: remove all <script>...</script> that appear after the last closing structural tag
    # and before </body>
    stitch_cleaned = re.sub(
        r'<script>\s*(?://|function\s|document\.|var\s|let\s|const\s|setInterval).*?</script>\s*(?=</body>)',
        '',
        stitch,
        flags=re.DOTALL
    )

    # Inject boilerplate scripts just before </body>
    injected = '\n'.join(scripts)
    # Use string .replace() to avoid regex $ issues
    merged = stitch_cleaned.replace('</body>', injected + '\n</body>', 1)

    with open(m["output"], "w", encoding="utf-8") as f:
        f.write(merged)

    print(f"  Written: {m['output']}\n")

print("=== All 3 files merged successfully! ===")
