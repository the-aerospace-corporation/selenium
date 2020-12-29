import os
import pandas as pd
class GetTelemetrySingleFile(object):
    def __init__(self, file_path):
        self.filename = os.path.basename(file_path)

