import os
import torch
from torch.utils.ffi import create_extension
from subprocess import call

this_file = os.path.dirname(os.path.realpath(__file__))
print(this_file)

sources = ['src/segment_reduction.c']
headers = ['src/segment_reduction.h']
defines = []
with_cuda = False
extra_objects = []

if torch.cuda.is_available():
  print('Including CUDA code.')
  sources += ['src/segment_reduction_cuda.c']
  headers += ['src/segment_reduction_cuda.h']
  defines += [('WITH_CUDA', None)]
  with_cuda = True

  extra_objects = ['src/cuda/segment_reduction.cu.o']
  extra_objects = [os.path.join(this_file, fname) for fname in extra_objects]

ffi = create_extension(
    '_ext.segment_reduction',
    headers=headers,
    sources=sources,
    define_macros=defines,
    relative_to=__file__,
    with_cuda=with_cuda,
    extra_objects=extra_objects,
    extra_compile_args=['-std=c11'])

if __name__ == '__main__':
  call('echo "Compiling segment reduction kernels by nvcc..."', shell=True)
  call(
      'nvcc -std=c++11 -c -o src/cuda/segment_reduction.cu.o src/cuda/segment_reduction.cu -x cu -Xcompiler -fPIC \
          -gencode arch=compute_35,code=sm_35 -gencode arch=compute_52,code=sm_52 -gencode arch=compute_60,code=sm_60 -gencode arch=compute_61,code=sm_61',
      shell=True)
  ffi.build()
