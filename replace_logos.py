import re

logos = {
    'mx': 'mixpane_trans.png',
    'in': 'intercom.png',
    'ji': 'jira_trans.png',
    'sf': 'salesforce.png',
    'zd': 'zendesk.png',
    'am': 'amplitude.png',
    'li': 'linear.png'
}

default_logos = ['mixpane_trans.png', 'intercom.png', 'jira_trans.png', 'salesforce.png', 'zendesk.png', 'amplitude.png', 'linear.png']

files = [
    r'c:\Users\EMMANUEL\OneDrive\Desktop\website\assets\mock code\decision-brain-mockup.html',
    r'c:\Users\EMMANUEL\OneDrive\Desktop\website\assets\videos\v1_clean.html',
    r'c:\Users\EMMANUEL\OneDrive\Desktop\website\assets\videos\v2_clean.html',
    r'c:\Users\EMMANUEL\OneDrive\Desktop\website\assets\videos\v3_clean.html'
]

fallback_idx = 0

def replace_base64_img(match):
    global fallback_idx
    tag = match.group(0)
    
    # We only want to replace if we actually see base64
    if 'base64' not in tag:
        return tag

    alt_match = re.search(r'alt="([^"]+)"', tag)
    if alt_match:
        alt = alt_match.group(1)
        logo_file = logos.get(alt, default_logos[0])
    else:
        logo_file = default_logos[fallback_idx % len(default_logos)]
        fallback_idx += 1
        
    new_src = f'../pictures/logos/{logo_file}'
    # match src="..." exactly
    new_tag = re.sub(r'src="[^"]+"', f'src="{new_src}"', tag)
    return new_tag

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        fallback_idx = 0
        new_content = re.sub(r'<img[^>]+>', replace_base64_img, content)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filepath}")
        else:
            print(f"No changes for {filepath}")
    except Exception as e:
        print(f"Error {filepath}: {e}")
