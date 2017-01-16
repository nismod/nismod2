"""Wraps the solid waste model using smif

Here we define how to run the model from Python, and connect the data defined
as inputs, outputs and assets with the simulation procedures in the model.
"""
import os
import inspect
from smif.sector_model import SectorModel


class SolidWasteModel(SectorModel):
    """Implements SectorModel so that the solid waste model can be run as part
    of a system of systems model
    """

    @staticmethod
    def current_folder():
        """Returns the path of the current file.
        """
        current_path = inspect.getfile(inspect.currentframe())
        return os.path.dirname(current_path)

    def get_model_executable(self):
        """Return path of current python interpreter
        """
        executable = 'models/solid_waste/bin/Debug/*/SolidWasteModel.dll'

        return os.path.join(self.current_folder(), executable)


    def get_results(self):
        """Gets the results from the model outputs and processes them
        """
        return results

    def simulate(self, decisions, state, data):
        """Runs the solid waste model
        """
        model_executable = self.get_model_executable()

        arguments = [model_executable,
                     "-sysfile={}".format(sysfile),
                     "-nodalfile={}".format(nodalfile),
                     "-save=g"]
        output = check_output(arguments)


        results = None
        if output:
            results = get_results()

        return results


    def extract_obj(self, results):
        """Implement this method to return a scalar value objective function

        This method should take the results from the output of the `simulate`
        method, process the results, and return a scalar value which can be
        used as the objective function

        Arguments
        =========
        results : :class:`dict`
            The results from the `simulate` method

        Returns
        =======
        float
            A scalar component generated from the simulation model results
        """
        pass