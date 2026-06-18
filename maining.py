import os

def generate_project_dump(output_file="project/project.txt"):
    # Создаем папку project, если её нет
    if not os.path.exists("project"):
        os.makedirs("project")
    
    # Исключаем лишние папки
    exclude_dirs = {'.git', 'venv', '__pycache__', 'session'}
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        # 1. Записываем дерево проекта
        outfile.write("PROJECT TREE:\n")
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            level = root.replace('.', '').count(os.sep)
            indent = ' ' * 4 * (level)
            outfile.write(f"{indent}{os.path.basename(root)}/\n")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                outfile.write(f"{subindent}{f}\n")
        
        outfile.write("\n" + "="*50 + "\n\n")
        
        # 2. Записываем содержимое файлов
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith(('.py', '.json', '.yaml', '.txt', '.md')):
                    file_path = os.path.join(root, file)
                    outfile.write(f"\nFILE: {file_path}\n")
                    outfile.write("-" * 30 + "\n")
                    
                    # Попытка чтения файла с разными кодировками
                    success = False
                    for enc in ['utf-8', 'utf-16', 'latin-1']:
                        try:
                            with open(file_path, "r", encoding=enc) as infile:
                                outfile.write(infile.read())
                            success = True
                            break
                        except (UnicodeDecodeError, Exception):
                            continue
                    
                    if not success:
                        outfile.write("Error: Could not read file with standard encodings.")
                        
                    outfile.write("\n" + "="*30 + "\n")

    print(f"Готово! Сводка проекта сохранена в {output_file}")

if __name__ == "__main__":
    generate_project_dump()