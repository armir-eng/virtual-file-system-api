## Virtual File System

This application mimics a file system, implementing its structure and all main interactions with it. <br>

It is based on an object-oriented design, representing the nodes with their basic metadata attributes and their relationships with each-other. <br>

The data is stored following a **rooted n-ary tree structure**, with an optimized search algorithm, to facilitate an efficient traversal, with a **linear complexity**:
- The linear complexity is achieved through the fact that each node is **only visited once** during the search operation, and  it is **proportional to the number of nodes** in the tree structure.

It also involves a **simple caching mechanism**, which speeds up searches for already accessed paths:
- The cache is implemented as a dictionary, mapping paths to their corresponding nodes, allowing for quick retrieval, with **O(1) complexity** for cache hits.  
<br>

The application is served through a **REST API**, allowing for easy interaction with the file system, based on **FastAPI** framework. Its endpoints define the main operations that can be performed on the file system, such as creating, reading, updating, and deleting files and directories. <br>

It also includes a **unit testing suite**, ensuring the reliability and correctness of the implemented features.


### Local Setup

The API can be installed and run locally by following these steps:

- Clone the repository: ```git clone https://github.com/armir-eng/virtual-file-system-api/```
- Navigate to the project directory: ```cd virtual-file-system-api```
- Create a virtual environment: ```python -m venv venv```
- Activate the virtual environment:
  - On Windows: ```venv\Scripts\activate```
  - On macOS/Linux: ```source venv/bin/activate```
- Install the required dependencies: ```pip install -r requirements.txt```
- Run the application: ```uvicorn main:app --reload```


### Unit tests execution
To run the unit tests, follow these steps:
- Ensure you are in the project directory and the virtual environment is activated.
- Run the tests suite using the command: ```pytest tests/unit_tests.py```