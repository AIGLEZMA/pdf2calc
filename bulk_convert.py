import os
import subprocess

input_folder = "Input"
output_folder = "Output"

files = os.listdir(input_folder)
total_size = sum(os.path.getsize(os.path.join(input_folder, f)) for f in files if os.path.isfile(os.path.join(input_folder, f)))
pdf_files = [f for f in files if f.lower().endswith(".pdf")]

print(f"📄 Number of files in '{input_folder}': {len(files)}")
print(f"📄 Total size: {total_size / (1024 * 1024):.2f} MB")

for pdf_file in pdf_files:
    input_pdf_path = os.path.join(input_folder, pdf_file)

    base_name = os.path.splitext(pdf_file)[0]

    words = base_name.split()
    truncated_name = " ".join(words[:16]) if len(words) > 16 else base_name

    cmd = [
        "python", "convert.py",
        truncated_name,
        input_pdf_path,
        output_folder,
        "prime",
        "false"
    ]

    print(f"\nRunning: {' '.join(cmd)}")
    subprocess.run(cmd)


