import re

files = [
    r'c:\Users\EMMANUEL\OneDrive\Desktop\website\assets\mock code\decision-brain-mockup.html',
    r'c:\Users\EMMANUEL\OneDrive\Desktop\website\assets\videos\v1_clean.html',
    r'c:\Users\EMMANUEL\OneDrive\Desktop\website\assets\videos\v2_clean.html',
    r'c:\Users\EMMANUEL\OneDrive\Desktop\website\assets\videos\v3_clean.html'
]

def replace_base64_img(match):
    tag = match.group(0)
    if 'base64' not in tag:
        return tag
        
    print(f"FOUND TAG: {tag[:50]}...{tag[-20:]}")
    new_tag = re.sub(r'src=[\'"][^\'"]+[\'"]', r'src="REPLACED"', tag)
    print(f"NEW TAG: {new_tag[:50]}...{new_tag[-20:]}")
    return new_tag

with open(files[0], 'r', encoding='utf-8') as f:
    content = f.read()

re.sub(r'<img[^>]+>', replace_base64_img, content)
