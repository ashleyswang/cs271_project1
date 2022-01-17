import time

class colors:
  INFO = '\033[90m'     # Grey
  NOTICE = '\033[34m'   # Blue
  SUCCESS = '\033[32m'  # Green
  FAIL = '\033[91m'     # Red
  ENDC = '\033[0m'      # Default


# Grey
def info(*args, **kwargs):
  debug_print(colors.INFO, *args, colors.ENDC, **kwargs)


# Blue
def notice(*args, **kwargs):
  debug_print(colors.NOTICE, *args, colors.ENDC, **kwargs)


# Green
def success(*args, **kwargs):
  debug_print(colors.SUCCESS, *args, colors.ENDC, **kwargs)


# Red
def fail(*args, **kwargs):
  debug_print(colors.FAIL, *args, colors.ENDC, **kwargs)


def debug_print(color=colors.ENDC, *args, **kwargs):
  timestamp = time.strftime("%H:%M:%S", time.localtime())
  print(f"{color}{timestamp}   ", *args, **kwargs)