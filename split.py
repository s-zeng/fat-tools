import os
import argparse
import shutil

fat_max = 4294901760 # 4GB
chunk_size = 32768 # relatively arbitrary chunk size

def part_name(name, index):
    return "part_{:02}_" + name

def write_part(file, folder, name, index, split_size=fat_max):
    with open(file, 'r+b') as open_file:
        file.seek(split_size*-1, os.SEEK_END)
        out_file = os.path.join(folder, part_name(name, index))

        written = 0

        print("Starting part {index}")

        with open(out_file, 'wb') as split:
            while written < split_size:
                split.write(open_file.read(chunk_size))
                written += chunk_size
        file.seek(split_size*-1, os.SEEK_END)
        file.truncate()
        print("Finished part {index}")
    return 0

def split(input_file):
    size = os.path.getsize(input_file)
    disk_info = shutil.disk_usage(os.path.dirname(os.path.abspath(input_file)))

    if disk_info.free < size:
        print("We need 4GB of space as buffer...")
        return 1

    num_splits = size//fat_max
    if num_splits < 1:
        print("This file fits on a FAT drive; no splits required")
        return 2
    else:
        print(f"Making {num_splits} splits")

    base_name = os.path.basename(input_file)

    out_folder = base_name + "_split"
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    shutil.move(input_file, os.path.join(out_folder, part_name(base_name, 0)))
    input_file = os.path.join(out_folder, part_name(base_name, 0))

    remainder = size%fat_max

    # write last part first
    write_part(input_file, out_folder, base_name, num_splits, split_size=remainder)

    for i in range(num_splits - 1):
        write_part(input_file, out_folder, base_name, num_splits - i - 1)

    print("Complete")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split large files to fit onto FAT32 drives")
    parser.add_argument("file_path", help="Path to file to split")

    args = parser.parse_args()

    if os.path.isfile(args.file_path):
        split(args.file_path)
    else:
        print("File not found")
