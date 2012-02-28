class LocalSettings(dict):
  def __init__(self, fname):
    f = open(fname)
    for line in f:
      if line.find('=') != -1:
        parts = line.split('=')
        parts[-1] = parts[-1][:-1]
        key = parts[0]
        val = ''.join(parts[1:])
        self[key] = val
