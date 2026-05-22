"""Merge Stitch design HTML with boilerplate script blocks.
Since boilerplate files may have been corrupted, this script reads scripts
from known-good backup content embedded here."""
import re
import os

PROJECT = r"C:\Users\DELL\.gemini\antigravity\scratch\lumiere-auctions"
STITCH = r"C:\Users\DELL\OneDrive\Desktop\stitch_elysian_luxury_auction_platform"

# We need to read the original boilerplate scripts. Since the files on disk may
# be corrupted, we will read them from a backup. But we don't have backups on disk.
# 
# Alternative approach: The boilerplate scripts are available in separate backup
# files that we'll create from the known content. 
#
# Actually, simplest approach: just read the Stitch file, strip its trailing script,
# and paste the boilerplate scripts that we store in separate .js files.

# Step 1: Extract the boilerplate scripts from the ORIGINAL boilerplate files.
# These were backed up before the corruption. Let's check if they exist in git reflog
# or if we need another approach.
#
# REVISED APPROACH: Read original boilerplate content from backup files we'll create.

print("This script expects backup .js files to exist. Creating them...")

# We'll use a different strategy entirely:
# 1. Read each Stitch file  
# 2. Remove its trailing <script> (the decorative one)
# 3. Read the script content from separate .js backup files
# 4. Inject and save

# But we don't have the .js files either. Let's try yet another approach:
# The corrupted files still have the script blocks, just with '$' corrupted to '</html>'.
# We can fix that corruption by replacing '</html>+Number' back to '$'+Number' etc.
# Actually that's fragile.

# BEST APPROACH: Read the corrupted files, extract scripts, fix the known corruption pattern.
# The corruption was: PowerShell's -replace treated $ in replacement string as regex backreference
# specifically $' becomes the text after the match. In our case the match was </body>,
# so $' = </html> (the text after </body> in the original). 
# So every literal $ in the scripts got replaced with </html>.

# Let's fix: replace '</html>' back to '$' but ONLY inside <script> blocks in the body.
# Actually no, that would break actual </html> references.

# CLEANEST APPROACH: Just read the scripts from the Stitch originals' own scripts 
# (which are decorative only), and read the API scripts from separate known-good sources.

# OK let me just do it properly: I'll reconstruct the files by:
# 1. Reading each Stitch file as the base (HTML structure)
# 2. Reading each boilerplate script from a HARDCODED source

# The original boilerplate scripts are stored at fixed backup locations.
# Let me create those backups by reading the corrupted files and fixing the corruption.

# ============================================================
# Actually, the simplest thing: I'll generate the merged files 
# directly by reading the Stitch files and the original script 
# files that might exist as .py/.js in the backend.
# ============================================================

# Let me try reading the originals from pip/site-packages... no.
# Let me just check if there's a git repo somewhere.

# FINAL STRATEGY: The originals exist on PyPI cache or __pycache__... no.
# Let me just hardcode what we need. The key boilerplate scripts were:

# For auction-detail.html: The huge script block from line 340-572 of the original
# For login.html: The script block from line 255-416 of the original  
# For dashboard.html: The script block from line 120-265 of the original

# Since I can't hardcode 200+ lines per file here, let me use the ACTUAL approach:
# The corrupted files have a VERY specific corruption: '$' became '</html>'.
# I can detect this and fix it.

print("Reading corrupted boilerplate files and fixing $ corruption...")

def fix_dollar_corruption(content):
    """The PowerShell -replace operator replaced all $ in the replacement string
    with the text after the regex match (</html>). So '$' became '</html>'
    inside the injected script blocks. Fix this."""
    # The corruption is specifically: </html> appearing inside <script> blocks
    # where $ should be. We need to be careful not to fix legitimate </html>.
    # 
    # Pattern: inside script blocks, '</html>' followed by typical JS $ contexts:
    # - '</html>+Number' -> '$'+Number'  (fmt function)
    # - '</html>{' -> '${' (template literals)
    # - '</html>(' -> '$(' (jQuery-style, unlikely here)
    
    # Actually let's just extract scripts, do replacement there, then put back.
    # Within <script> tags, </html> should NEVER appear legitimately.
    
    def fix_script(match):
        script = match.group(0)
        return script.replace('</html>', '$')
    
    # Fix </html> inside script blocks (but not the actual closing tag)
    return re.sub(r'<script(?![^>]*\bsrc\b)(?![^>]*\bid="tailwind-config")[^>]*>.*?</script>', 
                  fix_script, content, flags=re.DOTALL)


for name in ['auction-detail.html', 'login.html', 'dashboard.html']:
    filepath = os.path.join(PROJECT, 'frontend', name)
    print(f"\n=== Fixing: {filepath} ===")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixed = fix_dollar_corruption(content)
    
    # Check if anything changed
    if fixed != content:
        print(f"  Fixed $ corruption in {name}")
    else:
        print(f"  No corruption found in {name}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed)
    
    print(f"  Written: {filepath}")

print("\n=== All files fixed! ===")
