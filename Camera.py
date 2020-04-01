from io import BytesIO
from datetime import datetime
from PIL import Image

import os
import subprocess
import time
import numpy as np
import pandas as pd

# ToDo: move memory management to it's own class
    # add function to clean house once a week

class Camera():

    disk_space_to_reserve = 40 * 1024 * 1024 # Keep 40 mb free on disk

    def __init__(self, filepath):
        self.filepath = filepath

    def get_test_image(self):
        command = "raspistill -w 100 -h 75 -t 100 -e bmp -th none -o -"

        with BytesIO() as image_data:
            image_data.write(subprocess.check_output(command, shell=True))
            image_data.seek(0)
            img = Image.open(image_data)
            rgb = img.convert("RGB")
            array = np.array(rgb.getdata())

        df = pd.DataFrame(array, columns=['red', 'green', 'blue'])
        return df

    def save_image(self):
        self.keep_disk_space_free()
        time = datetime.now()
        t = time.strftime("%Y-%m-%d_%H:%M:%S")
        filename = self.filepath + "/"+ t +".jpg"
        command = "raspistill -ev -2 -t 100 -q 10 -a 12 -e jpg -o %s" % filename
        subprocess.call(command, shell=True)
        print("SAVING IMAGE %s" % filename)

    def image_to_dataframe(self, img):
        rgb = img.convert("RGB")
        array = np.array(rgb.getdata())
        df = pd.DataFrame(array, columns=['red', 'green', 'blue'])
        return df

    def compare_img_dfs(self, df1, df2):
        print(df1['red'].head())
        print(df2['red'].head())
        #changed_pixels = (img_df1['red'] != img_df2['red']).sum()
        changed_pixels= (abs(df1['red'] - df2['red']) > 3).sum()
        return changed_pixels

     # Keep free space above given level
    def keep_disk_space_free(self):
        if (self.get_free_space() < self.disk_space_to_reserve):
            for filename in sorted(os.listdir(self.filepath)):
                if filename.startswith("2020") and filename.endswith(".jpg"): # consider a unique filename beginning
                    os.remove(filename)
                    print("Deleted %s to avoid filling disk" % filename)
                    if (self.get_free_space() > self.disk_space_to_reserve):
                        return

     # Get available disk space
    def get_free_space(self):
        st = os.statvfs(self.filepath)
        du = st.f_bavail * st.f_frsize
        return du
