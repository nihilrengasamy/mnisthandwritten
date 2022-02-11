import PIL
from enum import Enum
from io import BytesIO, StringIO
from typing import Union
import pandas as pd
import streamlit as st
import numpy as np 
import json
import requests

STYLE = """
<style>
img {m
    max-width: 100%;
}
</style>
"""

FILE_TYPES = ["jpeg"]


class FileType(Enum):
    """Used to distinguish between file types"""

    IMAGE = "Image"
    CSV = "csv"
    PYTHON = "Python"


def get_file_type(file: Union[BytesIO, StringIO]) -> FileType:
    """The file uploader widget does not provide information on the type of file uploaded so we have
    to guess using rules or ML. See
    [Issue 896](https://github.com/streamlit/streamlit/issues/896)

    I've implemented rules for now :-)

    Arguments:
        file {Union[BytesIO, StringIO]} -- The file uploaded

    Returns:
        FileType -- A best guess of the file type
    """

    if isinstance(file, BytesIO):
        return FileType.IMAGE
    content = file.getvalue()
    if (
        content.startswith('"""')
        or "import" in content
        or "from " in content
        or "def " in content
        or "class " in content
        or "print(" in content
    ):
        return FileType.PYTHON

    return FileType.CSV


def main():
    """Run this function to display the Streamlit app"""
    st.markdown(STYLE, unsafe_allow_html=True)

    file = st.file_uploader("Upload file", type=FILE_TYPES)
    show_file = st.empty()
    if not file:
        show_file.info("Please upload a file of type: " + ", ".join(FILE_TYPES))
        return

    file_type = get_file_type(file)
    if file_type == FileType.IMAGE:
        show_file.image(file)
        print(file.name)
        
        pil_image = PIL.Image.open(file)
        img = pil_image.resize((28,28))

        img2arr = np.array(img)
        img2arr = img2arr / 255.0
        img2arr = img2arr.reshape(1,-1)

        #numpydata = input() 

        test = json.dumps({"data": img2arr.tolist()})

        # URL for the web service
        scoring_uri = 'http://5895b6eb-e70e-4fac-8abe-14b2db5b6257.centralindia.azurecontainer.io/score'
        # If the service is authenticated, set the key or token

        # Two sets of data to score, so we get two results back

        # Set the content type 
        headers = {'Content-Type': "application/json"}


        resp = requests.post(scoring_uri, test, headers=headers)
        print(resp.text)
        st.success(resp.text)
    file.close()


main()