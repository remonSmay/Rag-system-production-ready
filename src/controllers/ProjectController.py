import os 
# from controllers.BaseController import 
from controllers.BaseController import BaseController

from fastapi import UploadFile

from models import ResponseStatus

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()
    def get_project_path(self, project_id: str) -> str:
        """ for return the path for files stored 

        Args:
            project_id (str): project id the files 

        Returns:
            str: path to project files
        """
        
        project_id = os.path.join(self.files_dir, project_id)
        
        if not os.path.exists(project_id):
            os.makedirs(project_id)
        
        return project_id