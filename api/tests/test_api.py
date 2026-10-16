import base64
import io

# gives us bytesIO an in memory file so we can save an image 
# without touchign the disk
import torch

# needed for mte model test to biuld tensor of zeros
from fastapi.testclient import TestClient

# fake browser that calls your api directily in memory
# no serve is running
from PIL import Image

# Pillow used to create test image
from main import app, model
from model import CLASSES

client = TestClient(app)

# creates the fake browser client

def make_iamge_b64(color=(120, 120, 120)) -> str:
    buf = io.BytesIO() #creates an empty in memory file called buf buffer
    Image.new("RGB", (640, 480), color).save(buf, format="JPEG")

    # maeks iamge 640 480 filled with that color 
    # save jpeg into the in memory file instead of disk

    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

    #returns the image


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 # this must be true for the test to pass
    assert r.json() == {"status": "ok"} # json rurn the response into python dict

# Test valid image returns a valid label

def test_predict_return_valid_label():
    r = client.post("/predict-focus", json={"image_b64": make_iamge_b64()})
    assert r.status_code == 200
    assert r.json()["status"] in CLASSES

def test_rejects_bad_base64():
    r = client.post("/predict-focus", json={"image_b64": "not a base64 string"})

    assert r.status_code == 400

def test_rejects_non_image():
    payload = base64.b64encode(b"not an image").decode("utf-8")
    r = client.post("/predict-focus", json={"image_b64": payload})
    assert r.status_code == 400

def test_model_output_shape():
    with torch.no_grad(): # predicting not training no gradient tracking
        out = model(torch.zeros(1, 3, 64, 64)) # fake batch run thru pixels all 0
        assert out.shape == (1, 2) # assert the output shape is correct
        # one image 2 scores


