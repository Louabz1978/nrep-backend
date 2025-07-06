import os
import importlib

model_dir = os.path.dirname(__file__)
for file in os.listdir(model_dir):
    if file.endswith(".py") and file != "__init__.py":
        module_name = f"app.models.{file[:-3]}"
        importlib.import_module(module_name)