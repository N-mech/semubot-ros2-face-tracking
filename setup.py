from setuptools import find_packages, setup

package_name = 'neck_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='najm_faisal',
    maintainer_email='najm_faisal@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'vision_node = neck_control.vision_node:main',
            'pid_node = neck_control.pid_node:main',
            'hardware_node = neck_control.hardware_node:main',
        ],
    },
)
