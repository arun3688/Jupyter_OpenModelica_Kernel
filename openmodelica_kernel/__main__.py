from __future__ import absolute_import
from .kernel import *

if __name__ == '__main__':    
    try:
       from ipykernel.kernelapp import IPKernelApp
    except ImportError:
       from IPython.kernel.zmq.kernelapp import IPKernelApp
    
    IPKernelApp.launch_instance(kernel_class=OpenModelicaKernel)
