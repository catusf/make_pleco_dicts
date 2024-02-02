from bs4 import BeautifulSoup
import re
import glob
import os

INPUT_FOLDER = "html"
OUTPUT_FOLDER = "d:/htmlnew"

files = glob.glob(f"{INPUT_FOLDER}/*.html")

for file_path in files:
    path, filename = os.path.split(file_path)
    out_filepath = f"{OUTPUT_FOLDER}/{filename}"

    if os.path.exists(out_filepath):
        print(f"Skipped {file_path}")
        continue
    else:
        print(file_path)

    with open(file_path, "r", encoding="utf-8") as fread:
        html = fread.read()

        soup = BeautifulSoup(html, features="lxml")

        content_result = soup.find("div", class_="box-result")

        html = str(content_result)

        # Comment tag
        html = re.sub(r"<!--.+?-->", "", html, flags=re.DOTALL)
        html = re.sub(r'\s_ngcontent\-serverapp\-c\d+\=""', "", html, flags=re.DOTALL)

        # # Opening and closing tags
        # html = re.sub(r"<head.*?>.*?</head>", "", html, flags=re.DOTALL)
        # html = re.sub(r"<app-header.*?>.*?</app-header>", "", html, flags=re.DOTALL)
        # html = re.sub(r"<app-footer.*?>.*?</app-footer>", "", html, flags=re.DOTALL)
        # html = re.sub(r"<app-box-search.*?>.*?</app-box-search>", "", html, flags=re.DOTALL)
        # html = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.DOTALL)
        # html = re.sub(r"<textarea.*?>.*?</textarea>", "", html, flags=re.DOTALL)
        # html = re.sub(r"<sgv.*?>.*?</sgv>", "", html, flags=re.DOTALL)
        # html = re.sub(r"<button.*?>.*?</button>", "", html, flags=re.DOTALL)
        # # html=re.sub(r'<a.*?>.*?</a>','', html, flags=re.DOTALL)

        # # Only opening tag
        # html = re.sub(r"<img.*?>", "", html, flags=re.DOTALL)
        # html = re.sub(r"<input.*?>", "", html, flags=re.DOTALL)

        with open(out_filepath, "w", encoding="utf-8") as fwrite:
            fwrite.write(f"<html>\n{html}\n</html>")

        pass
