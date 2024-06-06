# The Black Sheep Challenge

## Overview

The "Black Sheep" challenge tests participants' ability to find a unique file among multiple files that share common characteristics. The task is to identify the unique file, which differs from the others in content, while the rest of the files have identical content but different names.

## Challenge Description

Participants will be provided with a ZIP file containing multiple files. Among these files, one will be unique in content, while the others will have the same content but different file names. The task is to locate this unique file.

## Solution Approaches

There are two primary methods to solve this challenge:

### 1. Directly Comparing the Binary Data

This method involves reading the binary data of each file and comparing them directly to find the unique file. While straightforward, this approach can be less efficient, especially with large files, as it involves reading and comparing potentially large amounts of data.

### 2. Comparing the Hash of the Files (Fingerprinting)

A more efficient approach is to use hash comparison. By calculating the hash (e.g., SHA-256) of each file, we can compare these hash values to identify the unique file. Hashing provides a compact representation of the file's content, making comparisons faster and more efficient.

## Using Hash Comparison to Find the Black Sheep

Below is a step-by-step explanation of how to use hash comparison to identify the unique file.

### Example Code

First, ensure you have Python installed. Then, use the following Python code:

```python
import shutil
from hashlib import sha256
from zipfile import ZipFile
from os import makedirs, listdir
from os.path import abspath, dirname, splitext, basename, join, exists


def hash_file(file_path):
    """Calculate the SHA-256 hash of the specified file."""
    sha256_hash = sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def extract_zip_file(zip_path):
    """Extracts the contents of a ZIP file to a specified directory."""
    directory_location = abspath(dirname(zip_path))
    folder_name = splitext(basename(zip_path))[0]
    extract_to = directory_location + "/" + folder_name
    makedirs(extract_to, exist_ok=True)

    with ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    return extract_to


def find_unique_file(folder):
    """Find the unique file in the provided folder based on its hash value."""
    try:
        files = [join(folder, file_name) for file_name in listdir(folder)]

        if len(files) < 3:
            raise ValueError("The folder must contain at least three files.")

        # Calculate hashes for the first three files
        hashes = [hash_file(file) for file in files[:3]]

        if hashes[0] == hashes[1] == hashes[2]:  # All three files have the same content
            common = hashes[0]
            # Find the unique file
            for file in files[3:]:
                if hash_file(file) != common:
                    return splitext(basename(file))[0]

        elif hashes[0] == hashes[1]:  # The third file is unique
            return splitext(basename(files[2]))[0]
        elif hashes[0] == hashes[2]:  # The second file is unique
            return splitext(basename(files[1]))[0]
        elif hashes[1] == hashes[2]:  # The first file is unique
            return splitext(basename(files[0]))[0]
    finally:
        if exists(folder):
            shutil.rmtree(folder)
    return "Unique file not found"


# Example usage
zip_path = "path_to_zip_file"
folder_path = extract_zip_file(zip_path)
unique_file = find_unique_file(folder_path)
print(f"Unique file: {unique_file}")
```

### Explanation

1. **Hash Calculation**: The `hash_file` function reads the file in binary mode and calculates its SHA-256 hash.
2. **Finding the Unique File**: The `find_unique_file` function calculates the hash values for the files and identifies the common hash value. It then compares the hashes of the remaining files to find the one that differs, indicating the unique file.

## Conclusion

The "Black Sheep" challenge is an exercise in file comparison and hashing. Using hash comparison is an efficient way to identify the unique file among many with identical content. This challenge enhances skills in file handling and data integrity verification, crucial for various data processing tasks.
