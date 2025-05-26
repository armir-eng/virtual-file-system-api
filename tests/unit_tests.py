import pytest
from file_system_structure import VirtualFileSystem


# This fixture initializes an empty VirtualFileSystem instance.
# It initializes a fresh file system for each test function that uses it.
# This ensures consistency and isolation between tests
@pytest.fixture
def fresh_vfs():
    return VirtualFileSystem()


def test_directory_creation(fresh_vfs: VirtualFileSystem):
    assert fresh_vfs.create_directory("/home") is True # Test directory creation in the root level
    assert fresh_vfs._get_node_object_by_path("/home") is not None # Test the existence of the directory after creation

    assert fresh_vfs.create_directory("/home/armir") is True # Test creation of a nested directory
    assert fresh_vfs._get_node_object_by_path("/home/armir") is not None # Test the existence of the nested directory after creation
    
    assert fresh_vfs.create_directory("/etc/documents") is False # Test creation of a nested directory in an existing one
    assert fresh_vfs._get_node_object_by_path("/etc/documents") is None

    assert fresh_vfs.create_directory("/home/documents/armir") is False # Test the creation of a directory in a non-existing parent directory
    assert fresh_vfs._get_node_object_by_path("/home/documents/armir") is None # Assert the inexistence of the directory after the failed creation


def test_file_creation(fresh_vfs: VirtualFileSystem):
    fresh_vfs.create_directory("/home")

    assert fresh_vfs.create_file("/hello.txt", b"Hello, World!") is True # Test creation of a file in the root level
    assert fresh_vfs._get_node_object_by_path("/hello.txt") is not None # Test the existence of the file after creation
    assert fresh_vfs.read_file("/hello.txt") == b"Hello, World!" # Test the content reading of the file

    assert fresh_vfs.create_file("/home/documents/sample.txt", b"Sample content") is False # Test creation of a file in a non-existing directory
    assert fresh_vfs._get_node_object_by_path("/home/documents/sample.txt") is None # Assert the inexistence of the file after the faild creation


def test_node_deletion(fresh_vfs: VirtualFileSystem):
    # Create initial directories
    fresh_vfs.create_directory("/home")
    fresh_vfs.create_directory("/home/armir")
    fresh_vfs.create_directory("/home/documents")
    fresh_vfs.create_directory("/home/work")
    fresh_vfs.create_directory("/home/work/management")
    fresh_vfs.create_file("/home/work/sample.txt", b"Sample content") # Create a file in the "/home/armir" directory

    # Test deletion of an existing directory
    assert fresh_vfs.delete("/home/armir") is True
    assert fresh_vfs._get_node_object_by_path("/home/armir") is None # This ensures that the directory is deleted

    # Test the deletion of a non-existing directory
    assert fresh_vfs.delete("/home/etc") is False
    
    # Test the deletion of a file in the non-yet deleted directory
    assert fresh_vfs.delete("/home/work/sample.txt") is True
    assert fresh_vfs._get_node_object_by_path("/home/work/sample.txt") is None # Test the file inexistence after deletion

    # Test the thorough deletion of a directory with children (the "/home" in this case, which has the "/documents" )
    assert fresh_vfs.delete("/home") is True
    assert fresh_vfs._get_node_object_by_path("/home") is None 
    assert fresh_vfs._get_node_object_by_path("/home/documents") is None # This ensures that the first-level nested children are also deleted
    assert fresh_vfs._get_node_object_by_path("/home/work/management") is None # Tests the deletion of a nested directory in a deeper level


def test_node_renaming(fresh_vfs: VirtualFileSystem):
    fresh_vfs.create_directory("/home")
    fresh_vfs.create_file("/home/sample.txt", b"Sample content") # Create a file in the "/home" directory

    # Test renaming of a directory
    assert fresh_vfs.rename("/home", "home1") is True
    assert fresh_vfs._get_node_object_by_path("/home1") is not None # Test the existence of the renamed directory
    assert fresh_vfs._get_node_object_by_path("/home") is None # Test the inexistence of the old directory name

    # Test renaming of a file
    assert fresh_vfs.rename("/home1/sample.txt", "sample_updated.txt") is True
    assert fresh_vfs._get_node_object_by_path("/home1/sample_updated.txt") is not None # Test the existence of the renamed file
    assert fresh_vfs._get_node_object_by_path("/home1/sample.txt") is None # Assert the inexistence of the old file name