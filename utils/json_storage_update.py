import json
from file_system_structure import VirtualFileSystem


def update_json_storage(vfs: VirtualFileSystem):
    # Update the file system status and write it to the JSON file storage
    file_system_status = {"/": vfs.to_dict()}
    with open("file_system_persisted_data.json", "w") as f:
        json_content = json.dumps(file_system_status, indent=2)
        f.write(json_content)