from dataclasses import dataclass
from time import perf_counter

import clip
import numpy as np
import torch
from tqdm import tqdm
from PIL import Image
import onnxruntime as ort



model, preprocess = clip.load("ViT-L/14", jit=True, device="cpu")

image_encoder = model.visual
print(preprocess)
x = torch.randn(1, 3, 224, 224)

model_name = "ViT-L_14.onnx"
# # Export the model
torch.onnx.export( 
    image_encoder,  # model being run
    x,  # model input (or a tuple for multiple inputs)
    model_name,  # where to save the model (can be a file or file-like object)
    opset_version=16,
    export_params=True,  # store the trained parameter weights inside the model file
    do_constant_folding= True,  # whether to execute constant folding for optimization
    input_names=["image"],  # the model's input names
    output_names=["output"],  # the model's output names
    dynamic_axes={
        "image": {0: "batch_size"},  # variable length axes
        "output": {0: "batch_size"},
    },
)

# let's check
print("Checking")

ort_session = ort.InferenceSession(model_name, providers=["CPUExecutionProvider"])
outputs = ort_session.run(None, {"image": x.numpy()})
print(outputs[0].shape)