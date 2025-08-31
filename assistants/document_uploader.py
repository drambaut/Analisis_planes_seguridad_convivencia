from pathlib import Path
from openai import AzureOpenAI

def upload_txt_file(client: AzureOpenAI, file_path: Path) -> str:
    with open(file_path, "rb") as f:
        file = client.files.create(file=f, purpose="assistants")
    print(f"Uploaded file: {file.id}")
    return file.id