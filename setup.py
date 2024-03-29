__author__ = 'andrea tramacere'

#!/usr/bin/env python

from setuptools import setup, find_packages
import  glob



f = open("./requirements.txt",'r')
install_req=f.readlines()
f.close()


packs=find_packages()

include_package_data=True

scripts_list=glob.glob('./bin/*')
setup(name='cdci_polar_plugin',
      version=1.0,
      description='A POLAR plugin  for CDCI online data analysis',
      author='Andrea Tramacere',
      author_email='andrea.tramacere@unige.ch',
      scripts=scripts_list,
      packages=packs,
      package_data={'cdci_polar_plugin':['config_dir/*']},
      include_package_data=True,
      install_requires=install_req,
)



