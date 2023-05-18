from setuptools import setup

setup(
    name='GPU Watcher',
    version='1.0',
    py_modules=['gpu_watcher'],
    entry_points={
        'console_scripts': [
            'gpuwatch = gpu_watcher:watch_gpus'
        ]
    },
    install_requires=[
    ]
)
