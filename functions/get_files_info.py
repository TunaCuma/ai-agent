import os


def get_files_info(working_directory, directory="."):
    full_path = os.path.join(working_directory, directory)

    if not os.path.isdir(full_path):
        raise Exception(f'Error: "{directory}" is not a directory')
    if not full_path.startswith(working_directory):
        raise Exception(
            f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        )

    file_infos = [
        {
            "file": file,
            "file_size": os.path.getsize(os.path.join(full_path, file)),
            "is_dir": os.path.isdir(os.path.join(full_path, file)),
        }
        for file in os.listdir(full_path)
    ]

    file_infos_string = "\n".join(
        [
            f"- {file_info['file']}: file_size={file_info['file_size']} bytes, is_dir={file_info['is_dir']}"
            for file_info in file_infos
        ]
    )

    return file_infos_string


print(get_files_info(os.path.abspath(""), "functions/"))

# print(os.path.abspath("aa"))
