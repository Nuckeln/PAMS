
import os
from pipreqs import pipreqs
import traceback

def read_file_content(file_name, encoding='utf-8'):
    try:
        with open(file_name, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        print(f"Fehlerhafte Datei übersprungen: {file_name}")
        return None

def get_all_imports(root, encoding='utf-8'):
    imports = set()
    for subdir, _, files in os.walk(root):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(subdir, file)
                content = read_file_content(file_path, encoding)
                if content:
                    imports.update(pipreqs.get_all_imports(file_path))
    return imports

def main():
    try:
        project_dir = "/Library/Python_local/Superdepot Reporting"  # Ihr Projektverzeichnis
        imports = get_all_imports(project_dir)
        pipreqs.output_requirements(imports, "requirements.txt")
        print("requirements.txt wurde erfolgreich erstellt.")
    except Exception as e:
        print("Fehler:", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()
