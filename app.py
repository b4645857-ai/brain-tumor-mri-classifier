import streamlit as st
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from pathlib import Path

st.set_page_config(
    page_title="Brain MRI Classifier",
    page_icon="🧠",
    layout="centered"
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "best_brain_tumor_mobilenetv2.keras"
CLASS_NAMES = ["glioma", "meningioma", "no_tumor", "pituitary"]

@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH.name}. "
            "Place the downloaded .keras file beside app.py."
        )
    return tf.keras.models.load_model(MODEL_PATH)

st.title("🧠 Brain Tumor MRI Classifier")
st.write(
    "An educational deep-learning prototype using MobileNetV2 to classify "
    "brain MRI images into four dataset categories."
)
st.info(
    "Educational/research use only. This application cannot diagnose brain tumours "
    "or replace assessment by a qualified medical professional."
)

uploaded_file = st.file_uploader(
    "Upload a brain MRI image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded MRI image", use_container_width=True)

        if st.button("Classify MRI", type="primary"):
            with st.spinner("Loading model and analysing image..."):
                resized = image.resize((224, 224))
                image_array = np.asarray(resized, dtype=np.float32)
                batch = np.expand_dims(image_array, axis=0)
                batch = preprocess_input(batch)

                model = load_model()
                probabilities = model.predict(batch, verbose=0)[0]
                predicted_index = int(np.argmax(probabilities))
                predicted_class = CLASS_NAMES[predicted_index]
                confidence = float(probabilities[predicted_index])

            st.subheader("Prediction result")
            st.metric(
                "Predicted dataset class",
                predicted_class.replace("_", " ").title()
            )
            st.write(f"Model confidence: **{confidence:.2%}**")

            st.subheader("Class probability scores")
            for name, probability in zip(CLASS_NAMES, probabilities):
                st.write(f"**{name.replace('_', ' ').title()}** — {probability:.2%}")
                st.progress(float(np.clip(probability, 0.0, 1.0)))

            st.caption(
                "These are model-generated probabilities, not clinical certainty. "
                "Predictions can be incorrect, including on genuine MRI images."
            )
    except Exception as error:
        st.error(f"Could not process this image: {error}")

st.divider()
st.caption(
    "Model: MobileNetV2 | Reported test accuracy on this project dataset: 90.24%. "
    "Dataset-specific result; not a guarantee of real-world diagnostic accuracy."
)
