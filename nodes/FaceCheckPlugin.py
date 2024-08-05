__version__ = "1.0"

from meshroom.core import desc
from pathlib import Path
from meshroom.core.plugin import PluginCommandLineNode, EnvType

class FaceCheckPlugin(PluginCommandLineNode):
    # On Windows, needs to avoid backslash for command line execution (as_posix needed)
    currentFilePath = Path(__file__).absolute()
    currentFileFolderPath = currentFilePath.parent

    # Get python environnement or global python
    # pythonPath = Path(os.environ.get("python"))
    pointsDrawerDirectory = (currentFileFolderPath / "../scripts/draw_points_comparison.py").resolve()

    size = desc.DynamicNodeSize("batch")
    # parallelization = desc.Parallelization(blockSize=50)

    envType = EnvType.VENV
    envFile = "/s/prods/research/io/in/from_prod/face_dataset/nodes/requirements.txt"
    
    # commandLine = "rez env blender -c 'blender -b {blendDirectoryValue} -P " + blenderRendererDirectory.as_posix() + " -P " + positionsExporterDirectory.as_posix() + " -P " + blendshapesExporterDirectory.as_posix() + " -- {seedValue} {outputFolderValue} {minFovValue} {maxFovValue} {batchValue}'" 
    # > /dev/null 2>&1'"

    category = 'Face dataset'
    documentation = ''''''

    inputs = [
        desc.File(
            name="inputImage",
            label="Inpainted File",
            description='''path to the inpainted files''',
            value="",
            uid=[],
            group="",
        ),
        desc.File(
            name="groundTruth",
            label="Ground Truth",
            description='''path to render directory containing ground truth''',
            value="",
            uid=[],
            group="",
        ),
        desc.IntParam(
            name='seed',
            label='Seed',
            description='''start frame to check''',
            value=1,
            range=(0, 1048574, 1),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='batch',
            label='Batch',
            description='''quantity of frames to check''',
            value=1,
            range=(0, 999999, 1),
            uid=[0],
            group=""
        ),
        desc.FloatParam(
            name='threshold',
            label='Monkey Face Threshold',
            description='''multiplier for morphology range''',
            value=0.5,
            range=(0.0, 1.0, 0.1),
            uid=[0],
            group=""
        ),
        desc.BoolParam(
            name='visibleOnly',
            label='Only Visible',
            description='''Use this option to display only non-culled points''',
            value=False,
            uid=[],
        ),

    ]
    outputs = [
        desc.File(
            name='outputFolder',
            label='Output Folder',
            description='''Output folder.''',
            value= lambda attr: desc.Node.internalFolder,
            uid=[],
            group=""
        ),
        desc.File(
            name='renderedFile',
            label='rendered file',
            description='''rendered file.''',
            value= desc.Node.internalFolder + "/face_check_*.png",
            semantic = "imageList",
            uid=[],
            group=""
        ),
    ]

    # /s/apps/users/multiview/meshroomVideoUtils/develop:/s/prods/research/io/in/from_prod/face_dataset
    def processChunk(self, chunk):
        seed = chunk.node.seed.value
        start = seed + chunk.range.start
        chunkSize = chunk.range.blockSize

        # if(start + chunkSize > chunk.node.batch.value):
        #     chunkSize = chunk.node.batch.value - start + 1

        if(start + chunkSize > chunk.node.batch.value + seed):
            chunkSize = chunk.node.batch.value + seed - start

        self.commandLine = "python " + self.pointsDrawerDirectory.as_posix() + " --seed " + str(start) + " --batch {batchValue} --inpaintDir {inputImageValue} --gtDir {groundTruthValue} --outPutDir {outputFolderValue} --threshold {thresholdValue} --visibleOnly {visibleOnlyValue}"
        
        super().processChunk(chunk)