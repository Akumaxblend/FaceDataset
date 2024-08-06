__version__ = "1.0"

from multiprocessing.connection import wait
from meshroom.core import desc
from meshroom.core.plugin import PluginCommandLineNode, EnvType
import os
from pathlib import Path
import psutil
import time


class FaceInpainterPlugin(PluginCommandLineNode):
    # On Windows, needs to avoid backslash for command line execution (as_posix needed)

    # Get python environnement or global python
    # pythonPath = Path(os.environ.get("python"))
    currentFilePath = Path(__file__).absolute()
    currentFileFolderPath = currentFilePath.parent
    faceInpainterDirectory = (currentFileFolderPath / "../scripts/random_face_inpainter.py").resolve()

    envType = EnvType.CONDA
    envFile = "/s/prods/research/io/in/from_prod/face_dataset/nodes/stable_diffusion_webui.yaml"

    size = desc.DynamicNodeSize("batch")
    # parallelization = desc.Parallelization(blockSize=2)
    # commandLine = 'python '+faceInpainterDirectory.as_posix() +' --inputDir {3dRenderDirectoryValue} --hairProbability {hairProbabilityValue} --eyebrowsProbability {eyebrowsProbabilityValue} --beardProbability {beardProbabilityValue} --clothProbability {clothProbabilityValue} --outputDir {outputFolderValue} --debug {debugInpaintValue} --seed {seedValue} --batch {batchValue}'

    category = 'Face dataset'
    documentation = ''''''

    inputs = [
        desc.File(
            name="3dRenderDirectory",
            label="3D render directory",
            description='''path to previously rendered face''',
            value="",
            uid=[],
            group="",
        ),
        desc.IntParam(
            name='seed',
            label='Seed',
            description='''Number of the first frame you want to inpaint''',
            value=1,
            range=(0, 1048574, 1),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='batch',
            label='Batch',
            description='''Total number of frames you want to inpaint. Make sure the folder numbers follow eachother''',
            value=1,
            range=(0, 999999, 1),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='eyebrowsProbability',
            label='Eyebrows Probability %',
            description='''Gamble percentage for inpainting eyebrows''',
            value=100,
            range=(0, 100, 1),
            uid=[0],
            group=""
        ),
        desc.FloatParam(
            name='eyebrowsDenoise',
            label='Eyebrows Denoise',
            description='''Denoising value for inpainting eyebrows: the higher, the more the output will be different from the input''',
            value=0.5,
            range=(0.0, 1.0, 0.05),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='hairProbability',
            label='Hair Probability %',
            description='''Gamble percentage for inpainting hair''',
            value=50,
            range=(0, 100, 1),
            uid=[0],
            group=""
        ),
        desc.FloatParam(
            name='hairDenoise',
            label='Hair Denoise',
            description='''Denoising value for inpainting hair: the higher, the more the output will be different from the input''',
            value=0.9,
            range=(0.0, 1.0, 0.05),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='beardProbability',
            label='Beard Probability %',
            description='''Gamble percentage for inpainting beard''',
            value=20,
            range=(0, 100, 1),
            uid=[0],
            group=""
        ),
        desc.FloatParam(
            name='beardDenoise',
            label='Beard Denoise',
            description='''Denoising value for inpainting beard: the higher, the more the output will be different from the input''',
            value=0.75,
            range=(0.0, 1.0, 0.05),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='clothProbability',
            label='Cloth Probability %',
            description='''Gamble percentage for inpainting hair''',
            value=100,
            range=(0, 100, 1),
            uid=[0],
            group=""
        ),
        desc.FloatParam(
            name='clothDenoise',
            label='Cloth Denoise',
            description='''Denoising value for inpainting cloth: the higher, the more the output will be different from the input''',
            value=1.0,
            range=(0.0, 1.0, 0.05),
            uid=[0],
            group=""
        ),
        desc.BoolParam(
            name='debugInpaint',
            label='Inpaint Debug',
            description='''Use this option to keep intermediate inpainting steps''',
            value=False,
            uid=[],
        ),
        desc.ChoiceParam(
            name='verboseLevel',
            label='Verbose Level',
            description='''verbosity level (critical, error, warning, info, debug).''',
            value='info',
            values=['critical', 'error', 'warning', 'info', 'debug'],
            exclusive=True,
            uid=[],
        ),
    ]

    outputs = [
        desc.File(
            name='outputFolder',
            label='Output Folder',
            description='''Output folder.''',
            value= desc.Node.internalFolder,
            uid=[],
            group=""
        ),
        desc.File(
            name='inpaintedFile',
            label='inpainted file',
            description='''inpainted file.''',
            value= desc.Node.internalFolder + "/inpaint_*.png",
            semantic = "imageList",
            uid=[],
            group=""
        ),
    ]


    # Partie rajoutée par Fabien pour qu'on puisse lancer stable au moment du compute du noeud d'inpainting
    def processChunk(self, chunk):
        chunk.logManager.start(chunk.node.verboseLevel.value)
        chunk.logger.info("Node executing")
        seed = chunk.node.seed.value
        start = seed + chunk.range.start
        chunkSize = chunk.range.blockSize

        isServerOpen = False

        if(start + chunkSize > chunk.node.batch.value + seed):
            chunkSize = chunk.node.batch.value + seed - start

        self.commandLine = 'python '+self.faceInpainterDirectory.as_posix() +' --inputDir {3dRenderDirectoryValue} --eyebrowsProbability {eyebrowsProbabilityValue} --eyebrowsDenoise {eyebrowsDenoiseValue} --hairProbability {hairProbabilityValue} --hairDenoise {hairDenoiseValue} --beardProbability {beardProbabilityValue} --beardDenoise {beardDenoiseValue} --clothProbability {clothProbabilityValue} --clothDenoise {clothDenoiseValue} --outputDir {outputFolderValue} --debug {debugInpaintValue} --seed '+str(start)+' --batch {batchValue}'

        stableCmd = ["/s/apps/users/vernam/stable_diffusion/stable-diffusion-webui/webui.sh", "--api", "--api-server-stop", "--skip-torch-cuda-test"] # The --api-server-stop enables the stop route so we can POST /sdapi/v1/server-kill to kill the server
        try:
            stableServerProc = psutil.Popen(stableCmd, cwd=chunk.node.internalFolder)

            import urllib3 # Importing here to ensure being in the conda environment

            while(isServerOpen is False):
                try:
                    chunk.logger.info(urllib3.request(url="http://127.0.0.1:7860", method="GET", retries=False))
                    chunk.logger.info("###   Stable diffusion started successfuly!   ###")
                    time.sleep(5) # Time margin to ensure non-cutting the loading process
                    isServerOpen = True
                except:
                    chunk.logger.info("###   Waiting for stable diffusion to launch   ###")
                    time.sleep(5)

            super().processChunk(chunk)
            try:
                urllib3.request(url="http://127.0.0.1:7860/sdapi/v1/server-kill", method="POST") # Ensures the server is killed by api
            except:
                chunk.logger.info("###   Apparent issue with server closing but successfuly closed ?   ###")
            stableServerProc.kill()
        except psutil.Error:
            chunk.logger.error("###   Issue with stable diffusion starting   ###")
            chunk.logManager.stop()
            return False

    # /s/apps/users/multiview/meshroomVideoUtils/develop:/s/prods/research/io/in/from_prod/face_dataset