__version__ = "1.0"

from meshroom.core import desc
import os
from pathlib import Path

class FaceRenderer(desc.CommandLineNode):
    # On Windows, needs to avoid backslash for command line execution (as_posix needed)
    currentFilePath = Path(__file__).absolute()
    currentFileFolderPath = currentFilePath.parent

    # Get python environnement or global python
    # pythonPath = Path(os.environ.get("python"))
    blenderRendererDirectory = (currentFileFolderPath / "../scripts/random_face_renderer.py").resolve()
    positionsExporterDirectory = (currentFileFolderPath / "../scripts/vertices_positions_single_image.py").resolve()
    blendshapesExporterDirectory = (currentFileFolderPath / "../scripts/shape_keys_exporter_single_frame.py").resolve()

    size = desc.DynamicNodeSize("batch")
    parallelization = desc.Parallelization(blockSize=50)

    # commandLine = "rez env blender -c 'blender -b {blendDirectoryValue} -P " + blenderRendererDirectory.as_posix() + " -P " + positionsExporterDirectory.as_posix() + " -P " + blendshapesExporterDirectory.as_posix() + " -- {seedValue} {outputFolderValue} {minFovValue} {maxFovValue} {batchValue}'" 
    # > /dev/null 2>&1'"

    category = 'Face dataset'
    documentation = ''''''

    inputs = [
        desc.File(
            name="blendDirectory",
            label="Blend Directory",
            description='''path to blender file''',
            value="/s/prods/research/io/in/from_prod/face_dataset/blends/face_dataset_template.blend",
            uid=[],
            group="",
        ),
        desc.IntParam(
            name='seed',
            label='Seed',
            description='''requested frame to render by Blender''',
            value=1,
            range=(0, 1048574, 1),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='batch',
            label='Batch',
            description='''quantity of frames to render by Blender''',
            value=1,
            range=(0, 999999, 1),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='minFov',
            label='Minimum FOV',
            description='''minimum fov value of blender camera''',
            value=8,
            range=(0, 499, 1),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='maxFov',
            label='Maximum FOV',
            description='''maximum fov value of blender camera''',
            value=200,
            range=(1, 500, 1),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='camAmplitudeX',
            label='Camera Amplitude X',
            description='''rotation amplitude for the camera on the x axis (x=right)''',
            value=90,
            range=(0, 180, 1),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='camAmplitudeY',
            label='Camera Amplitude Y',
            description='''rotation amplitude for the camera on the y axis (y=camera axis)''',
            value=90,
            range=(0, 180, 1),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='camAmplitudeZ',
            label='Camera Amplitude Z',
            description='''rotation amplitude for the camera on the z axis (z=up)''',
            value=90,
            range=(0, 180, 1),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='worldAmplitudeX',
            label='World Amplitude X',
            description='''rotation amplitude for the HDRI on the x axis (x=right)''',
            value=0,
            range=(0, 180, 1),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='worldAmplitudeY',
            label='World Amplitude Y',
            description='''rotation amplitude for the HDRI on the y axis (y=camera axis)''',
            value=0,
            range=(0, 180, 1),
            uid=[0],
            group=""
        ),
        desc.IntParam(
            name='worldAmplitudeZ',
            label='World Amplitude Z',
            description='''rotation amplitude for the HDRI on the z axis (z=up)''',
            value=0,
            range=(0, 180, 1),
            uid=[0],
            group=""
        ),
        desc.FloatParam(
            name='modelRange',
            label='3DMM range',
            description='''multiplier for morphology range''',
            value=0.85,
            range=(0.0, 5.0, 0.05),
            uid=[0],
            group=""
        ),

        desc.FloatParam(
            name='expressionRangeMin',
            label='Minimum Expression Value',
            description='''minimum value to use as coefficient for the expression blendshapes''',
            value=0.0,
            range=(0.0, 1.0, 0.05),
            uid=[0],
            group=""
        ),
        desc.FloatParam(
            name='expressionRangeMax',
            label='Maximum Expression Value',
            description='''maximum value to use as coefficient for the expression blendshapes''',
            value=1.0,
            range=(0.0, 1.0, 0.05),
            uid=[0],
            group=""
        ),
        desc.FloatParam(
            name='modelOffsetX',
            label='Model Offset X',
            description='''offset of the model on the x axis (x=right)''',
            value=0.0,
            range=(-30.0, 30.0, 0.1),
            uid=[0],
            group=""
        ),
        desc.FloatParam(
            name='modelOffsetY',
            label='Model Offset Y',
            description='''offset of the model on the y axis (y=camera axis)''',
            value=0.0,
            range=(-30.0, 30.0, 0.1),
            uid=[0],
            group=""
        ),
        desc.FloatParam(
            name='modelOffsetZ',
            label='Model Offset Z',
            description='''offset of the model on the z axis (z=up)''',
            value=0.0,
            range=(-30.0, 30.0, 0.1),
            uid=[0],
            group=""
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
            value= lambda attr: desc.Node.internalFolder,
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

        self.commandLine = "rez env blender -c 'blender -b {blendDirectoryValue} -P " + self.blenderRendererDirectory.as_posix() + " -- " + str(start) + " {outputFolderValue} {minFovValue} {maxFovValue} " + str(chunkSize) + " {modelRangeValue} {modelOffsetXValue} {modelOffsetYValue} {modelOffsetZValue} {expressionRangeMinValue} {expressionRangeMaxValue} {camAmplitudeXValue} {camAmplitudeYValue} {camAmplitudeZValue} {worldAmplitudeXValue} {worldAmplitudeYValue} {worldAmplitudeZValue}'"
        super(FaceRenderer, self).processChunk(chunk)