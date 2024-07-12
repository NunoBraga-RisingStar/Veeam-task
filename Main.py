import os
import sys
import shutil
import time
import hashlib
import argparse
from datetime import datetime

def calculate_md5(file_path):
    """
    Calculate the MD5 hash of a file.
    This is used to check if the files are identical.
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def log_operation(message, log_file):
    """
    Log operations to a file and print to the console.
    Each log entry is timestamped.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(log_file, 'a') as log:
        log.write(log_message + "\n")

def sync_folders(source, replica, log_file):
    """
    Synchronize the contents of the source folder to the replica folder.
    Ensure that the replica folder becomes an exact copy of the source folder.
    Log all file operations.
    """
    source_files = set(os.listdir(source))
    replica_files = set(os.listdir(replica))

    # Copy or update files from source to replica
    for item in source_files:
        source_item = os.path.join(source, item)
        replica_item = os.path.join(replica, item)

        if os.path.isdir(source_item):
            if not os.path.exists(replica_item):
                shutil.copytree(source_item, replica_item)
                log_operation(f"Directory created: {replica_item}", log_file)
            else:
                sync_folders(source_item, replica_item, log_file)
        else:
            if not os.path.exists(replica_item) or calculate_md5(source_item) != calculate_md5(replica_item):
                shutil.copy2(source_item, replica_item)
                log_operation(f"File copied/updated: {replica_item}", log_file)

    # Remove files from replica that are not in source
    for item in replica_files:
        replica_item = os.path.join(replica, item)
        source_item = os.path.join(source, item)

        if item not in source_files:
            if os.path.isdir(replica_item):
                shutil.rmtree(replica_item)
                log_operation(f"Directory removed: {replica_item}", log_file)
            else:
                os.remove(replica_item)
                log_operation(f"File removed: {replica_item}", log_file)

def main():
    """
    Main function to parse command line arguments and start the synchronization loop.
    """
    parser = argparse.ArgumentParser(description="Folder Synchronization Script")
    parser.add_argument('source', help="Path to the source folder")
    parser.add_argument('replica', help="Path to the replica folder")
    parser.add_argument('interval', type=int, help="Synchronization interval in seconds")
    parser.add_argument('log_file', help="Path to the log file")
    args = parser.parse_args()

    source = args.source
    replica = args.replica
    interval = args.interval
    log_file = args.log_file

    # Synchronize folders periodically
    try:
        while True:
            sync_folders(source, replica, log_file)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Program was interrupted by user. Exiting...")
        sys.exit()


if __name__ == "__main__":
    main()
