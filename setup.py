import sys

from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(
  packages = [], excludes = [],
  includes = ['atexit'],
)

name = 'PositionOCR'

if sys.platform == 'win32':
  name = name + '.exe'

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
  # Executable('line_ocr.py', base = base, targetName = name, compress = True)
  Executable('line_ocr.py', base = base, targetName = name)
]

setup(name='PositionOCR',
      version = '1.0',
      description = 'Image descrition OCR. Store into a xlsx file.',
      options = dict(build_exe = buildOptions),
      executables = executables)
