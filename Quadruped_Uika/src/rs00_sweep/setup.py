from glob import glob
from setuptools import find_packages, setup

package_name = 'rs00_sweep'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config',
         glob('config/*.yaml')),
        ('share/' + package_name + '/launch',
         glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='lzh',
    maintainer_email='maintainer@example.com',
    description='Single motor frequency sweep tools for RS00 motor tests.',
    license='TODO',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'single_motor_sweep = rs00_sweep.single_motor_sweep:main',
        ],
    },
)
