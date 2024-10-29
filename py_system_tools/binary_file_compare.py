import os
from pathlib import Path


def compare_file_contents(
    file_path1: Path, file_path2: Path, batch_size: int = 8
) -> dict[int, tuple[bytes, bytes]]:
    """Compares the binary contents of two files byte by byte.

    Args:
        file_path1 (Path): Path to the first file.
        file_path2 (Path): Path to the second file.
        batch_size (int): Number of bytes to read at a time.

    Returns:
        dict: A dictionary with byte addresses as keys, where differences were found.
            The values are tuples with the byte values from each file.

    #TODO/PERF:
        import bincmp
        differences = bincmp.diff("file1.bin", "file2.bin")
    """
    differences = dict[int, tuple[bytes, bytes]]()

    # Check if the files are the same size before comparison
    size1 = file_path1.stat().st_size
    size2 = file_path2.stat().st_size

    if size1 != size2:
        print(f"Files {file_path1} and {file_path2} are of different sizes.")
        return differences

    # Open both files and compare byte by byte
    with open(file_path1, "rb") as f1, open(file_path2, "rb") as f2:
        byte_address = 0
        while True:
            byte1 = f1.read(batch_size)
            byte2 = f2.read(batch_size)

            # If both bytes are empty, we've reached the end of both files
            if not byte1 and not byte2:
                break

            # Compare the bytes and record differences
            if byte1 != byte2:
                differences[byte_address] = (byte1, byte2)

            byte_address += batch_size

    return differences


def compare_folders(folder1: Path, folder2: Path, batch_size: int = 8):
    """Compares files with the same names in two folders, outputting byte differences.

    Args:
        folder1 (Path): Path to the first folder.
        folder2 (Path): Path to the second folder.

    """
    # List all files in both folders
    files1 = set(os.listdir(folder1))
    files2 = set(os.listdir(folder2))

    # Find common files in both folders
    common_files = files1.intersection(files2)

    # Compare each common file
    for file_name in common_files:
        path1 = folder1 / file_name
        path2 = folder2 / file_name

        # Ensure both are files
        if not os.path.isfile(path1):
            print(f"File {path1} not found in {folder1}")
            continue
        if not os.path.isfile(path2):
            print(f"File {path2} not found in {folder2}")
            continue

        print(f"Comparing {file_name}...")
        differences: dict[int, tuple[bytes, bytes]] = compare_file_contents(
            path1, path2, batch_size
        )

        # Output differences or state of equality
        if differences:
            print(f"Differences found in {file_name}:")
            # if len(differences) == 6: # we expected 6 differences,
            # mb change to a call back function here
            #     print(f"  {len(differences)} differences found.")
            #     continue
            for addr, (val1, val2) in differences.items():
                print(f"  Byte {addr}: {val1} vs {val2}")
        else:
            print(f"{file_name} is identical in both folders.")


# Example usage
# compare_folders("/path/to/folder1", "/path/to/folder2")
if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    if len(args) != 2:
        print("Usage: python binary_file_compare.py folder1 folder2")
    else:
        compare_folders(Path(args[0]), Path(args[1]), 1)
