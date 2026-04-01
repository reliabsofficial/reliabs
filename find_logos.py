import re

files = [
    r'c:\Users\EMMANUEL\OneDrive\Desktop\website\assets\mock code\decision-brain-mockup.html',
    r'c:\Users\EMMANUEL\OneDrive\Desktop\website\assets\videos\v1_clean.html',
    r'c:\Users\EMMANUEL\OneDrive\Desktop\website\assets\videos\v2_clean.html',
    r'c:\Users\EMMANUEL\OneDrive\Desktop\website\assets\videos\v3_clean.html'
]

with open('logo_info.txt', 'w', encoding='utf-8') as out:
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            out.write(f"--- {filepath} ---\n")
            img_tags = re.findall(r'<img[^>]*>', content)
            for tag in img_tags:
                if 'base64' in tag:
                    tag_preview = re.sub(r'data:image/[^;]+;base64,[^"]+', 'BASE64', tag)
                    out.write(tag_preview + '\n')
        except Exception as e:
            out.write(f"Error reading {filepath}: {e}\n")
