import os
from meshroom.core.plugin import PluginNode, PluginCommandLineNode, EnvType

class DummyVenv(PluginNode):

    category = 'Dummy'
    documentation = ''' '''

    envType = EnvType.VENV
    envFile = os.path.join(os.path.dirname(__file__), "requirements.txt")

    inputs = []
    outputs = []

    def processChunk(self, chunk):
        import numpy as np
        chunk.logManager.start("info")
        chunk.logger.info(np.abs(-1))