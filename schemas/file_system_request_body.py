from pydantic import BaseModel


class BaseRequestBody(BaseModel):
    path: str


class FileOperationRequestBody(BaseRequestBody):
    """
        File operation requests inherit the path and have the extra content field.
    """
    content: str


class RenameRequestBody(BaseModel):
    """
        The node renaming request will have this specific structure among others.
    """
    old_path: str
    new_name: str