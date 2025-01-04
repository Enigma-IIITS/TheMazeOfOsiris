# The Invisible Man Challenge

## Overview

The "Invisible Man" challenge tests participants' ability to navigate through files and directories with non-printable (invisible) characters in their names. The goal is to find a specific file hidden among others and count the total number of characters within that file.

## Challenge Description

Participants will be given a ZIP file containing multiple nested directories and files. Among these files, one will have a name composed entirely of invisible characters. The task is to locate this file, whose name will be provided in the question, and determine the total count of characters inside it, including any invisible characters.

## Solution Approach

To successfully complete the challenge, participants can follow these steps:

1. **Extract the ZIP File**: Unzip the provided file to a directory on your computer.
2. **Locate the File with Invisible Characters**: Use file browsing tools or scripts to identify the specified file with a name consisting of non-printable characters.
3. **Count the Characters**: Open the located file and count all characters in the file content, including invisible ones.

### Example Code

Below is an example code snippet demonstrating how to locate the file with invisible characters and count its contents using Python.

First, ensure you have Python installed. Then, use the following Python code:

```python
import shutil
from zipfile import ZipFile
from os import makedirs, walk
from os.path import abspath, dirname, splitext, basename, join, exists

def extract_zip_file(zip_path):
    """Extracts the contents of a ZIP file to a specified directory."""
    directory_location = abspath(dirname(zip_path))
    folder_name = splitext(basename(zip_path))[0]
    extract_to = directory_location + "/" + folder_name
    makedirs(extract_to, exist_ok=True)

    with ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    return extract_to

def find_count(folder, target_filename):
    try:
        for root, _, files in walk(folder):
            if target_filename in files:
                file_location = join(root, target_filename)
                with open(file_location, "r", encoding="utf-8") as file:
                    content = file.read()
                    return len(content)
    finally:
        if exists(folder):
            shutil.rmtree(folder)
    return 0

# Example usage
zip_path = "path_to_zip_file"
folder_path = extract_zip_file(zip_path)
target_filename = "\ufeff"  

# Get the character count in the file
character_count = find_count(folder_path, target_filename)
print(f"Total number of characters in the file: {character_count}")
```

## Conclusion

The "Invisible Man" challenge is an exercise in file system navigation and character handling. By utilizing file browsing tools or scripting, participants can efficiently locate the hidden file with invisible characters and determine the total count of characters in the file content. This challenge enhances skills in file management and character encoding, crucial for handling various data processing tasks.
