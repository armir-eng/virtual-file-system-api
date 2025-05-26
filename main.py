from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import re

from file_system_structure import VirtualFileSystem
from schemas.file_system_request_body import BaseRequestBody, FileOperationRequestBody, RenameRequestBody
from utils.json_storage_update import update_json_storage


app: FastAPI = FastAPI()
router: APIRouter = APIRouter(prefix="/fs", tags=["File system endpoints"])

# Add CORS middleware to the app
# Have to allow all origins, as it is impossible to know the frontend Google Cloud service URL in advance.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Read the JSON storage of the system structure map
# This will serve as a persistence mean to make sure the frontend is in sync with the file system status in backend
with open("file_system_persisted_data.json", "r") as f:
    file_system_data = json.load(f)

# If the file system has an empty content, instantiate its data structure and initialize the JSON storage.
if not file_system_data:
    vfs = VirtualFileSystem()
    update_json_storage(vfs)

else:
    # Initialize the file system structure with the persisted data in the JSON storage
    # The deserialization static method `from_dict()` will construct the object from the JSON stroge.
    vfs: VirtualFileSystem = VirtualFileSystem().from_dict(file_system_data)


@router.get("/data")
async def retrieve_file_system_data():
    """
        This endpoint gets the file system data to be loaded in the frontend
    """
    with open("file_system_persisted_data.json", "r") as f:
        data = json.load(f)
    
    return JSONResponse(status_code=200, content = data)


@router.post("/directory/create")
async def create_directory(request_body: BaseRequestBody):
    """
        This endpoint performs the directory creation in the file system.
    """
    vfs.create_directory(request_body.path)

    # Update the file system status and write it to the JSON file storage
    update_json_storage(vfs)

    # Extract the file name and involve it in the success response message
    _, directory_name = vfs._get_parent_directory_and_name(request_body.path)
    return JSONResponse(status_code=200, content={"message": f"'{directory_name}' was successfully created!"})


@router.post("/delete")
async def delete_node(request_body: BaseRequestBody):
    """
        This endpoint performs the item deletionin the file system.
    """
    vfs.delete(request_body.path)

    update_json_storage(vfs)

    # Extract the file name and involve it in the success response message
    _, directory_name = vfs._get_parent_directory_and_name(request_body.path)
    return JSONResponse(status_code=200, content={"message": f"'{directory_name}' was successfully created!"})


@router.post("/rename")
async def rename_node(request_body: RenameRequestBody):
    """
        This endpoint performs the item renaming in the file system.
    """
    _, old_name = vfs._get_parent_directory_and_name(request_body.old_path)
    vfs.rename(request_body.old_path, request_body.new_name)

    update_json_storage(vfs)
    
    new_path = re.sub(r"\/(?!.*\/).*", "/"+ request_body.new_name, request_body.old_path) # Replace the last part of the path with the new name
    _, new_name = vfs._get_parent_directory_and_name(new_path)
    return JSONResponse(status_code=200, content={"message": f"'{old_name}' was successfully renamed to {new_name}!"})


@router.post("/file/write")
async def create_file(request_body: FileOperationRequestBody):
    
    """
        This endpoint performs the file creation in the file system.
    """
    # Create the file if it does not exist
    vfs.create_file(request_body.path, request_body.content)

    # Write the content to the file
    vfs.write_file(request_body.path, request_body.content.encode("utf-8"))
    
    update_json_storage(vfs)
    
    # Extract the file name and involve it in the success response message
    _, file_name = vfs._get_parent_directory_and_name(request_body.path)
    return JSONResponse(status_code=200, content={"message": f"'{file_name}' was successfully created!"})


app.include_router(router)