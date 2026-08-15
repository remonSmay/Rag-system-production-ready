from controllers import ProjectController
from controllers.BaseController import BaseController
from controllers.ProjectController import ProjectController
from fastapi import UploadFile

from models import ResponseStatus

import os
import re


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024  # MB to Bytes

    def validate_upload_file(self, file: UploadFile):
        if not file.content_type:
            return False, ResponseStatus.FILE_NOT_CONTENT_TYPE.value

        allowed_types = self.app_settings.FILE_ALLOWED_TYPES or []
        if file.content_type not in allowed_types:
            return False, ResponseStatus.FILE_TYPE_NOT_ALLOWED.value
        if (
            file.size is not None
            and self.app_settings.FILE_MAX_SIZE is not None
            and file.size > (self.app_settings.FILE_MAX_SIZE * self.size_scale)
        ):
            return False, ResponseStatus.FILE_SIZE_EXCEEDED.value

        return True, ResponseStatus.FILE_VALIDATION_SUCCESS.value

    def get_unique_filepath(self, original_filename: str, project_id: str):
        """  make the random file path and random_key and cleaned file 

        Args:
            original_filename (str): the file name the file from user 
            project_id (str): the id of file 

        Returns:
            new file name (list): return the new file after add the random (eg.( 32423423efdgdf_file.txt )
        """
        
        random_key = self.generate_random_string()
        
        project_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_file_name = self.clean_file_name(orig_file_name=original_filename)

        new_file_path = os.path.join(project_path, random_key + "_" + cleaned_file_name)

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path, random_key + "_" + cleaned_file_name
            )

        return new_file_path, random_key + "_" + cleaned_file_name

    def clean_file_name(self, orig_file_name: str) -> str:

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r"[^\w.]", "", orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name
