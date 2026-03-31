with open('src/backend/main.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = 0
for i, line in enumerate(lines):
    if skip > 0:
        skip -= 1
        continue

    if 'full_text = ""' in line and i+4 < len(lines):
        new_lines.append('        full_text = " ".join([segment.text for segment in segments]).strip()\n')
        skip = 4 # Skip the next 4 lines (for, full_text +=, empty line, strip)
    else:
        new_lines.append(line)

with open('src/backend/main.py', 'w') as f:
    f.writelines(new_lines)
