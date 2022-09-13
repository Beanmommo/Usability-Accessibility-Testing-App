from venv import create
from resources.resource import resource, resource_types 
from abc import ABC, abstractmethod
from atexit import register
import os
import requests

from typing import TypeVar, Generic, List, Callable, Dict
from resources.resource import ResourceGroup, ResourceWrapper
from resources.resource_types import ResourceType

class TaskMetaclass(type):
    def __new__(meta, name, bases, attrs):
        TaskFactory._tasks[name] = cls = type.__new__(meta, name, bases, attrs)
        return cls

class TaskFactory:
    _tasks = {}

    @classmethod
    def create_tasks(names : List[str], resource_groups : Dict[ResourceType, ResourceGroup]) -> None:
        all_names = names

        for name in names:
            cls = TaskFactory._tasks[name]
            assert cls is not None

            req_inputs = cls.get_input_types()
            depends = TaskFactory.get_tasks_with_outputs(req_inputs)

            all_names += depends
            

        unique_names = list(set(all_names))

        for name in unique_names:
            cls = TaskFactory._tasks[name]
            assert cls is not None

            cls(resource_groups)


    @classmethod
    def get_tasks_with_outputs(resource_types : List[ResourceType]) -> List[str]:
        names = []

        for type in resource_types:
            for task in TaskFactory._tasks:
                if type in task.get_output_types():
                    names.append(task.get_name())

        return list(set(names))







class Task(ABC, metaclass=TaskMetaclass):
    """Class to manage an algorithm."""
    
    def __init__(self) -> None:
        super().__init__()
        ##self.output_dir = output_dir
        ##if not os.path.exists(self.output_dir):
        ##    os.makedirs(self.output_dir)
        

    @abstractmethod
    @classmethod
    def get_name(self) -> str:
        """Name of the task"""
        return
    
    @abstractmethod
    @classmethod
    def get_input_types(self) -> List[ResourceType]:
        """Input resource types of the task"""
        return

    @abstractmethod
    @classmethod
    def get_output_types(self) -> List[ResourceType]:
        """Output resource types of the task"""
        return


    
    @abstractmethod
    def get_output_dir(self) -> str:
        """Output directory of the task"""
        return 



    @classmethod
    def http_request(self, url, body):
        """Makes a http request with url and body
        
        returns response body
        """
        response = None
        error = None
        
        try: 
            request = requests.Session()
            response = request.post(url, json=body)
            return response
        
        except Exception as e:
            error = str(e)
            print("ERROR ON REQUEST: " + error)
        
        return response
