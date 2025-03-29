import os
import hashlib
import pickle

def initialize_vcs():
    """Initialize the Version Control System by creating necessary storage directory."""
    os.makedirs('.vcs_repository', exist_ok=True)
    print("Version Control System has been initialized.")

def create_snapshot(directory):
    """Create a snapshot of the specified directory and store it."""
    # Create a SHA-256 hash to uniquely represent the snapshot
    snapshot_hash = hashlib.sha256()
    
    # Dictionary to store the snapshot details, including file contents
    snapshot_info = {'files': {}}

    # Walk through the directory and capture file content
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Skip files that are part of the version control system's storage
            if '.vcs_repository' in os.path.join(root, file):
                continue
            # Get the full path for the file
            file_path = os.path.join(root, file)
            # Read the content of the file in binary mode
            with open(file_path, 'rb') as file_obj:
                content = file_obj.read()
                # Update the snapshot hash with the content of the file
                snapshot_hash.update(content)
                # Store the content of the file in the snapshot data
                snapshot_info['files'][file_path] = content

    # Generate the final hash value for the snapshot
    snapshot_id = snapshot_hash.hexdigest()
    
    # Add the list of files that were part of this snapshot
    snapshot_info['file_paths'] = list(snapshot_info['files'].keys())
    
    # Serialize and store the snapshot to a file named after its hash
    with open(f'.vcs_repository/{snapshot_id}', 'wb') as snapshot_file:
        pickle.dump(snapshot_info, snapshot_file)

    # Output confirmation with the snapshot's unique identifier
    print(f"Snapshot successfully created with identifier {snapshot_id}")

def restore_snapshot(snapshot_id):
    """Restore the files from the given snapshot."""
    snapshot_file_path = f'.vcs_repository/{snapshot_id}'
    
    # Check if the snapshot exists, otherwise notify the user
    if not os.path.exists(snapshot_file_path):
        print("Error: Snapshot not found.")
        return

    # Load the snapshot data from the file
    with open(snapshot_file_path, 'rb') as snapshot_file:
        snapshot_data = pickle.load(snapshot_file)

    # Restore each file from the snapshot
    for file_path, content in snapshot_data['files'].items():
        # Ensure the directory for the file exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Write the file content back to restore its original state
        with open(file_path, 'wb') as file_obj:
            file_obj.write(content)

    # Identify and remove files that are no longer part of the snapshot
    current_files_set = set()
    for root, dirs, files in os.walk('.', topdown=True):
        if '.vcs_repository' in root:
            continue
        for file in files:
            current_files_set.add(os.path.join(root, file))

    snapshot_files_set = set(snapshot_data['file_paths'])
    files_to_remove = current_files_set - snapshot_files_set

    # Delete any extraneous files that are not part of the snapshot
    for file_path in files_to_remove:
        os.remove(file_path)
        print(f"File {file_path} has been removed.")

    # Output confirmation of reverting to the snapshot
    print(f"Reverted successfully to snapshot with ID {snapshot_id}")

if __name__ == "__main__":
    import sys
    command = sys.argv[1]

    # Execute the appropriate function based on the command provided
    if command == "init":
        initialize_vcs()
    elif command == "snapshot":
        create_snapshot('.')
    elif command == "revert":
        restore_snapshot(sys.argv[2])
    else:
        print("Unknown command. Please use 'init', 'snapshot', or 'revert'.")
