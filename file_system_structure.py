from typing import Dict, Union, List, Any, Optional, Tuple
from datetime import datetime
import re


# This virtual file system will be designed in an OOP style
# There will be three classes that well-represent a file system and its components
# 1- A generic class that represents any node
###  - It contains all attributes that node types (files and directories) have in common.
###  - It will also serve as a parent class for the ones respectively dedicated to file and folder nodes
# 2- A class that represents a directory node
# 3- A class that represents a file node
# 4- The main class that represents the file system
### - Methods defined in it cover all the basic CRUD actions on nodes


class FileSystemNode:

    """
        This class will be the generic representation of a file system node
        It will serve as the parent of classes specifically dedicated to files and directories
        Its attributes are the ones that are common to all nodes
    """
    def __init__(self, name: str, parent:Union["DirectoryNode", None] = None):
        self.name = name
        self.parent = parent

        # These attributes store the metadata of nodes
        # These values are initialized at the moment a file system node is created
        # That is why they are equally set to the current time 
        self.created = datetime.now()
        self.modified = self.created
        self.accessed = self.created

    # This method will update the timestamp metadata of a file system node (creation, access or modification time) 
    # We just provide it the field name, and it will accordingly update its value
    def update_timestamp_metadata(self, metadata_field: str):
        setattr(self, metadata_field, datetime.now())

    def update_modified_time(self):
        self.update_timestamp_metadata("modified")
        
        # Propagate the modification time to the parent directory, if the node has one.
        if self.parent:
            self.parent.update_timestamp_metadata("modified")

    def to_metadata(self)-> dict:
        metadata = {
            "created": self.created.isoformat(),
            "accessed": self.accessed.isoformat(),
            "modified": self.modified.isoformat(),
            "type": "directory" if isinstance(self, DirectoryNode) else "file" 
        }

        if isinstance(self, FileNode):
            metadata["size"] = self.size
            metadata["content"] = self.content.decode('utf-8') if isinstance(self.content, bytes) else self.content
        
        return metadata


class FileNode(FileSystemNode):
    """
        A file system node will be represented by this class
        The content of a file is stored in the 'content' attribute.
        The 'children' attribute is a dictionary that stores the children of a directory.        
    """
    def __init__(self, name: str, parent=None, content: bytes = b""):
        super().__init__(name, parent)
        self.content = content
        self.size = len(content) # Content has to be set to 'bytes' type, as it shows the actual size of a content.

    def read(self)-> bytes:
        self.update_timestamp_metadata("accessed")
        return self.content
    
    def write(self, content: bytes)-> None:
        self.content = content
        self.size = len(content)
        self.update_timestamp_metadata("created")
        self.update_timestamp_metadata("modified")
        self.update_timestamp_metadata("accessed")

    def to_dict(self)-> dict:
        data = self.to_metadata()
        data["size"] = self.size
        data["content"] = self.content
        return data
    

class DirectoryNode(FileSystemNode):
    """
        This class represents a directory node in the file system
    """

    def __init__(self, name: str, parent=None):
        super().__init__(name, parent)
        self.children: Dict[str, Union[FileSystemNode]] = {} # This dictionary facilitates the O(1) for the child lookup, by just using its name.

    def add_child(self, child: FileSystemNode) -> None:
        """Adds a child node to the directory and assigns its parent attribute to the parent directory object."""
        self.children[child.name] = child
        child.parent = self
        self.update_timestamp_metadata("modified")

    def remove_child(self, child_name: str) -> None:
        """
            Removes a child from a parent directory node by its name.
            The complexity is O(1) for the lookup, and O(n) for the deletion, where n is the number of child nodes.
        """
        if child_name in self.children:
            del self.children[child_name]
            self.update_timestamp_metadata("modified")
    
    def get_child(self, child_name: str)-> Union[FileSystemNode, None]:
        """
            Retrieves a child node by its name, and returns None if it does not exist.
            The complexity is normally O(1) for the lookup, but it can be O(n) in the worst case, where n is the number of children.       
        """
        return self.children.get(child_name)
    
    def list_children(self) -> List[str]:
        """
            Lists the names of all children nodes in the directory.
            The complexity is O(n), where n is the number of children.
        """
        return list(self.children.keys())
    
    def to_dict(self)-> dict:
        """
            This is the directory node objects serializer method.
            It utilizes the 'to_metadata()' helper method to retrieve the common metadata attributes.
            The key part of this method is the recursion of the children nodes serialization.
            This offers an O(n) complexity, where n is the number of nodes.
        """
        data = self.to_metadata()
        data["children"] = {
            child_name: (child.to_dict() if isinstance(child, DirectoryNode) else child.to_metadata())
            for child_name, child in self.children.items()
        }
        return data


class VirtualFileSystem:
    
    """
        This is the main class that represents the virtual file system
        Its instantiation comes with a root directory
        It contains the methods to operate on nodes
        A special attribute of it is the cache hashmap, which helps in achieving the O(1) complexity for searching the already traversed paths.
    """
    def __init__(self):
        """
            The file system structure is initialized with the root directory node.
            It is immediately added also into the traversal cache map.      
        """ 
        self.root = DirectoryNode("/")
        self.traversal_cache: Dict[str, FileSystemNode] = {"/": self.root}

    
    def _normalize_path(self, path: str)-> str:
        """
            This internal utility method makes sure the path provided is adjusted conforming to a standard (normalized) form.
            It checks for trailing '/' characters, omitting them, so the path parts are correctly extracted.
            It also makes sure evey path starts with the leading '/' character (mocking the Unix systems path convention)
            The complexity of this method is O(n), where n is the length of the path string.
        """

        # If path is empty, let "/" be it 
        if not path:
            path = "/"
        
        # Normalize the paths where the leading "/" is missing
        if not path.startswith("/"):
            path = "/" + path

        # Remove the trailing slash, except for the root directory case
        if path != "/" and path.endswith("/"):
            path = path[:-1]
        
        return path
    

    def _get_node_object_by_path(self, path: str)-> Optional[FileSystemNode]:
        """
            This internal helper method retrieves the FileSystemNode object, parsing the path provided.
            It provides an:
            - O(1) complexity, if the path is cached.
            - O(depth_size), if it is not.
        """

        path = self._normalize_path(path)

        # Instantly retrieve the object stored in the traversal cache, if the path is stored there.
        if path in self.traversal_cache:
            return self.traversal_cache[path]
        

        # Traverse the path, if it is not cached.
        if path == "/":
            return self.root
        
        else:
            # Perform the traversal, based on directory nodes.

            path_parts = path.strip("/").split("/") # List out the path parts, removing the leading and trailing slashes
            current = self.root # Start the directory traversal with the root node. This variable will be updated to nested nodes during the path traversal. 
        
            for part in path_parts:
                
                # If the path part encountered is an empty string, the path must be a incorrectly provided.
                # This way, the function has to signal a retrieval failure, returing None.
                if not part:
                    return None
                
                # If the current node object is not a DirectoryNode, we are facing another edge-case, where a path must be incorrectly provided.
                # In example: it may be provided as "/a/b.txt/b", where a file precedes a directory. 
                if not isinstance(current, DirectoryNode):
                    return None

                # Retrieve the child object. Return None, if it does not exist.
                # This means, there is a non-existing directory or file, part of a path, trying to be accessed. 
                current = current.get_child(part)
                if current is None:
                    return None
                
            self.traversal_cache[path] = current
            return current
        
    def _get_parent_directory_and_name(self, path: str) -> Tuple[Optional[DirectoryNode], str]:
        """
            This is an internal method that will be utilized by the CRUD operation methods.
            It makes sure every node is accurately localized inside its parent and correctly operated on.
            This method's complexity is depended on the '_get_node_object_by_path()'.
        """
        normalized_path = self._normalize_path(path)

        if path == "/":
            return None, ""
        
        parent_path = re.search(r".*(?=\/(?!.*\/))", normalized_path).group()
        name = re.search(r"\/(?!.*\/).*$", path).group().replace("/","")

        parent_dir_object = self._get_node_object_by_path(parent_path)

        if parent_dir_object is None or not isinstance(parent_dir_object, DirectoryNode):
            return None, name
        
        return parent_dir_object, name
    
    def _remove_changed_node_from_cache(self, cached_path: str)-> None:
        """
            This method releases the cache map from the changed nodes.
            The complexity of this method is O(n) (worse case), where n is the number of cached paths.
        """
        normalized_path = self._normalize_path(cached_path)

        # Remove the provided path, and all its possible nested paths
        # In this case there is a trick: We need to be careful in the dictionary traversal.
        # If we directly iterate over the dictionary, we will face the classical "RuntimeError: dictionary changed size during iteration"
        # This way, we create a copy of the dictionary keys, iterate over it and safely delete the items from the original dictionary.
        for cached_path in list(self.traversal_cache):
            if cached_path == normalized_path or cached_path.startswith(normalized_path + "/"):
                del self.traversal_cache[cached_path]


    # The methods below are dedicated to the CRUD operations on the file system nodes.
    
    def create_file(self, path: str, content: bytes='')-> bool:
        """
            This method creates a new file, if it does not exists, and fails if it does (returns False).
            The complexity of this method is O(depth), where depth is the number of directories in the path.
        """
        normalized_path = self._normalize_path(path)

        parent_dir, file_name = self._get_parent_directory_and_name(path)

        # If user has provided an incorrect path, then the function evaluates to False.
        if parent_dir is None:
            return False
        
        # If a file with the provided name already exists, the creation has to fail. 
        if file_name in parent_dir.children:
            return False
        
        # Create the new FileNode object, and add its association into the parent directory's object children map.
        new_file = FileNode(file_name, parent=parent_dir, content=content)
        parent_dir.add_child(new_file)
        
        # Cache the path to facilitate the quick future access
        self.traversal_cache[normalized_path] = new_file
        return True

    def read_file(self, path: str)-> Optional[bytes]:
        """
            This method reads the content of a file if it exists.
            It will be used in the unit tests to verify the file creation correctness.
            This method offers: 
              - O(depth) for the lookup (where depth is the number of directories in the path).
              - O(content_size) for the reading operation. 
        """
        file_object = self._get_node_object_by_path(path)

        if file_object is None or not isinstance(file_object, FileNode):
            return None

        if isinstance(file_object, FileNode):
            return file_object.read()


    def write_file(self, path: str, content: bytes)-> bool:
        """
            This method writes a new content in an existing file, create a new one if it does not exist.
            It provides an O(depth) complexity for the lookup, and O(content_size) for the writing operation 
        """
        file_object = self._get_node_object_by_path(path)

        # If the file does not exist in the system, create it.
        if file_object is None:
            parent_dir, file_name = self._get_parent_directory_and_name(path)

            # If the parent dir does not exist, the file writing operation fails
            if parent_dir is None:
                return False

            # Create the new file and add it into the parent directory's childrens list.
            new_file = FileNode(file_name, parent=parent_dir, content=content)
            parent_dir.add_child(new_file)
            
            # Cache the file path for fast future access (O(1) lookup complexity)
            self.traversal_cache[self._normalize_path(path)]=new_file
            
            return True
        
        # If the path provided does not belong to a file, fail the operation.
        if not isinstance(file_object, FileNode):
            return False
        
        file_object.write(content)
        return True
    
    
    def create_directory(self, path: str)-> bool:
        """
            This method creates a new directory if it does not exist, else fails.
        """

        parent_dir, dir_name = self._get_parent_directory_and_name(path)

        if parent_dir is None:
            return False
        
        if dir_name in parent_dir.children:
            return False
        
        new_dir = DirectoryNode(dir_name, parent=parent_dir)
        parent_dir.add_child(new_dir)

        self.traversal_cache[self._normalize_path(path)] = new_dir
        
        return True
    
    
    def delete(self, path: str)-> bool:
        """
            This method accordingly deletes a file system node, differentiating the directory and file cases.
            The root directory is prevented to be deleted.
            The path of the deleted item is also omitted from the cache map. 
        """

        parent_dir, node_name = self._get_parent_directory_and_name(path)

        # If the parent directory is incorrectly provided, the deletion fails.
        if parent_dir is None:
            return False
        
        node_object = self._get_node_object_by_path(path)
        
        # If the node with the specified path does not exist, the deletion fails.
        # This will come in handy in the test, when we try to delete a non-existing node. 
        if node_object is None:
            return False
        
        # The root directory cannot be deleted
        if node_object is self.root:
            return False
        
        parent_dir.remove_child(node_name)
        self.traversal_cache[self._normalize_path(path)] = node_object
        
        self._remove_changed_node_from_cache(path)
        parent_dir.update_timestamp_metadata("modified") # Signal the parent directory that one of its children has been deleted
        
        return True
    
    
    def rename(self, path: str, new_name: str)-> bool:
        """
            This is the node renaming operation method.
            It simply
        """
        parent_dir, node_name = self._get_parent_directory_and_name(path)

        if parent_dir is None:
            return False
        
        node_object = parent_dir.get_child(node_name)
        
        # Fail if the node with the specified name does not exist
        if node_object is None:
            return False
        
        # The node will be replaced by removing its existing entry in the parent directory's childrens map.
        # Then the updated node will change its name attribute, and be reinserted in the childrens map with the updated name.
        parent_dir.remove_child(node_object.name)
        
        
        # Change the name attribute of the renamed node and reinsert it into the parent directory
        node_object.name = new_name
        parent_dir.add_child(node_object)
        
        # Update the traversal cache with the new name
        self._remove_changed_node_from_cache(path)  # Remove the old path from the cache
        new_path = re.sub(r"\/(?!.*\/).*", "/"+ new_name, path) 
        self.traversal_cache[self._normalize_path(new_path)] = node_object # Update the cache with the new path

        return True
    

    # The below methods will be used for the persistence mechanism of the file system data state.
    # A JSON file will be used to store the file system state data.
    # The data will be serialized for storage during CRUD operations and deserialized for retrieval in the client side 

       
    def to_dict(self)-> dict:
        """
            This method serves the serializer of the file system state data
            The data generated will be dumped to the JSON storage, which will persist the file system state.
        """
        return self.root.to_dict()
    
    @staticmethod
    def from_dict(data: Dict[str, Any])-> "VirtualFileSystem":
        """
            This method will be used to deserialize the JSON storage data into the file system main class
            When the application starts, the persisted data will be read and the file system will be constructed from it.
            The usefulness is noticed when the application is restarted, and the client's work is stored to where it was left.

        """

        def _construct_node(name: str, data: Dict[str, Any], parent:Optional[DirectoryNode] = None) -> FileSystemNode:
            """
                This is the internal method that constructs the node objects
                For directories, a recursive process is executed to generate all the nested children nodes.
                This offers a O(n) complexity, where n is the number of nodes in the file system.
                The reason for this is that every node is only visited once, and the recursion depth is limited to the number of nodes. 
            """
            created = datetime.fromisoformat(data["created"])
            accessed = datetime.fromisoformat(data["accessed"])
            modified = datetime.fromisoformat(data["modified"])

            node_type = data["type"]

            if node_type == "file":
                file_node = FileNode(name, parent=parent, content=b"")
                file_node.created = created
                file_node.accessed = accessed
                file_node.modified = modified

                if "size" in data:
                    file_node.size = data["size"]
                if "content" in data:
                    content = data["content"]
                    file_node.content = content.encode("utf-8") if isinstance(content, str) else content
                
                return file_node

            elif node_type == "directory":
                dir_node = DirectoryNode(name, parent=parent)

                dir_node.created = created
                dir_node.accessed = accessed
                dir_node.modified = modified

                children_object: dict = data.get("children", {})
                for child_name, child_data in children_object.items():
                    child_node = _construct_node(child_name, child_data, parent = dir_node)
                    dir_node.add_child(child_node)
                
                return dir_node
        
        # Cache all the persisted data
        def _cache_persisted_data(node: FileSystemNode, current_path: str):
            """
                This internal method caches the persisted data.
                It is called recursively for directory nodes, and adds the first-level node into the cache map.
                The complexity of this method is O(n), where n is the number of nodes in the file system.
            """
            # Add the first-level node into the cache map, at first. 
            vfs.traversal_cache[current_path] = node

            # If it is a directory, then recursively add all childrens' paths in cache.
            if isinstance(node, DirectoryNode):
            
                for child_name, child_node in node.children.items():
                    child_path = current_path.rstrip("/") + "/" + "/" + child_name if current_path != "/" else "/" + child_name
                    _cache_persisted_data(child_node, child_path)
        
        
        vfs = VirtualFileSystem() # The file system instance is initialized
        root_name = list(data.keys())[0] # The root directory name is extracted from the JSON storage data
        root_data = data[root_name] # The root directory data is extracted from the JSON storage
        vfs.root = _construct_node(root_name, root_data) # The nodes will recursively be constructed, starting from the root directory.
        _cache_persisted_data(vfs.root, "/") # The cache map is populated with the root directory and its children nodes.
        
        return vfs