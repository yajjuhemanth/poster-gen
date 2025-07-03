import os
import streamlit as st
from PIL import Image
import pytesseract
import vertexai
from vertexai.language_models import TextGenerationModel, TextEmbeddingModel
from vertexai.generative_models import GenerativeModel

# Initialize Vertex AI (assumes GOOGLE_APPLICATION_CREDENTIALS is set)
vertexai.init(project="poster", location="us-central1")

st.set_page_config(page_title="Adaptive Poster Generator", layout="centered")
st.title("🎨 AI Poster Generator (Gemini & Imagen via Vertex AI)")

user_prompt = st.text_input("Enter your base poster prompt:")
uploaded_file = st.file_uploader("Or upload an image for context:", type=["png", "jpg", "jpeg"])
generate = st.button("Generate Poster")

if generate:
    if not user_prompt and not uploaded_file:
        st.error("Please provide a text prompt or upload an image.")
    else:
        improved_text = user_prompt
        context_info = ""

        # Step 1: Improve prompt with Gemini
        if user_prompt:
            with st.spinner("Refining your prompt with Gemini 2.5 Flash..."):
                model = TextGenerationModel.from_pretrained("gemini-2.5-flash")
                response = model.predict(
                    f"Please improve this marketing poster prompt:\n{user_prompt}",
                    temperature=0.7,
                    max_output_tokens=256,
                )
                improved_text = response.text

        # Step 2: OCR and content from image
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)

            ocr_text = pytesseract.image_to_string(image)
            context_info += f"Text from image: {ocr_text.strip()}\n"

            with st.spinner("Describing image with Gemini 2.5 Flash..."):
                desc_response = model.predict(
                    f"Here is the text extracted: {ocr_text}\nDescribe the image and suggest how to incorporate it into the poster.",
                    temperature=0.7,
                    max_output_tokens=256,
                )
                context_info += f"Image context: {desc_response.text.strip()}\n"

        # Step 3: Final poster prompt
        final_prompt = (
            f"Create a poster design.\n"
            f"Title/Concept: {improved_text.strip()}\n"
            f"{context_info}"
        )

        # Step 4: Generate poster image with Imagen
        with st.spinner("Generating poster image with Imagen..."):
            img_model = GenerativeModel("imagen-4")
            img_resp = img_model.generate_content(
                final_prompt,
                generation_config={
                    "candidate_count": 1,
                    "image_size": "1024x1024"
                }
            )
            # The image is usually in the 'content' attribute as a base64 string
            import base64
            from io import BytesIO

            # Extract the base64 string from the Content object
            content_obj = img_resp.candidates[0].content
            if hasattr(content_obj, "text"):
                image_b64 = content_obj.text
            else:
                image_b64 = str(content_obj)
            image_bytes = base64.b64decode(image_b64)
            poster = Image.open(BytesIO(image_bytes))
            st.image(poster, caption="🖼 Generated Poster", use_column_width=True)

        with st.expander("See final prompt"):
            st.code(final_prompt)