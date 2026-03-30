with open('src/frontend/app.js', 'r') as f:
    content = f.read()

import re
# Remove the unused variables and outdated comment lines
content = re.sub(r'\s*const originalText = data\.original_text;\s*const ipaText = data\.ipa_text; // Needs to be sent by backend\s*', '\n            ', content)

with open('src/frontend/app.js', 'w') as f:
    f.write(content)
