# image_fun_app.py
import streamlit as st
from PIL import Image, ImageFilter, ImageOps # Import necessary Pillow modules
import io # For handling image bytes

# --- Configuration ---
st.set_page_config(page_title="Pillow Image Fun", layout="wide")
st.title("🎨 Pillow Image Fun")
st.subheader("Upload an image and apply cool effects!")

# --- Session State Initialization ---
# To store the original uploaded image bytes and the Pillow Image object
if 'original_image_bytes' not in st.session_state:
    st.session_state.original_image_bytes = None
if 'original_pil_image' not in st.session_state:
    st.session_state.original_pil_image = None
if 'processed_pil_image' not in st.session_state:
    st.session_state.processed_pil_image = None
if 'last_uploaded_filename' not in st.session_state: # To track if a new file is uploaded
    st.session_state.last_uploaded_filename = None

# --- Image Caching Function ---
@st.cache_data # Cache the image loading and initial processing
def load_image(image_bytes):
    """Loads an image from bytes and returns a Pillow Image object."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        return img
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

# --- Sidebar for Upload ---
with st.sidebar:
    st.header("🖼️ Upload Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Check if a new file has been uploaded
        if st.session_state.last_uploaded_filename != uploaded_file.name:
            st.session_state.original_image_bytes = uploaded_file.getvalue()
            st.session_state.original_pil_image = load_image(st.session_state.original_image_bytes)
            # Reset processed image when a new image is uploaded
            st.session_state.processed_pil_image = st.session_state.original_pil_image
            st.session_state.last_uploaded_filename = uploaded_file.name
            st.success(f"'{uploaded_file.name}' loaded!")

# --- Main Area for Image Display ---
if st.session_state.original_pil_image:
    st.subheader("Your Image:")
    col1, col2 = st.columns(2)
    with col1:
        st.image(st.session_state.original_pil_image, caption="Original Image", use_container_width=True)
    with col2:
        # Initially, processed image is the same as original
        if st.session_state.processed_pil_image:
            st.image(st.session_state.processed_pil_image, caption="Processed Image", use_container_width=True)
        else:
            st.image(st.session_state.original_pil_image, caption="Processed Image (No effects yet)", use_container_width=True)
    
    st.sidebar.header("✨ Apply Effects")

    # --- Effect Selection ---
    effect_options = ["None", "Grayscale", "Sepia", "Blur", "Sharpen", "Contour", "Emboss", "Edge Enhance"]
    selected_effect = st.sidebar.selectbox("Choose an effect:", effect_options)

    # --- Rotation Control ---
    rotation_angle = st.sidebar.slider("Rotate Image (°):", -180, 180, 0, 5) # Min, Max, Default, Step

    # --- Flip Controls ---
    flip_horizontal = st.sidebar.checkbox("Flip Horizontal")
    flip_vertical = st.sidebar.checkbox("Flip Vertical")

    # --- Apply Button (or can be live) ---
    if st.sidebar.button("Apply Effects & Rotation", key="apply_button"):
        if st.session_state.original_pil_image:
            current_image = st.session_state.original_pil_image.copy() # Start fresh from original for each apply

            # 1. Apply selected effect
            if selected_effect == "Grayscale":
                current_image = ImageOps.grayscale(current_image)
            elif selected_effect == "Sepia": # Simple Sepia
                sepia_filter = [
                    0.393, 0.769, 0.189, 0,
                    0.349, 0.686, 0.168, 0,
                    0.272, 0.534, 0.131, 0
                ]
                current_image = current_image.convert("RGB") # Ensure it's RGB for matrix
                current_image = current_image.convert("L", matrix=sepia_filter) # Apply sepia toning
                current_image = current_image.convert("RGB") # Convert back for display
            elif selected_effect == "Blur":
                current_image = current_image.filter(ImageFilter.BLUR)
            elif selected_effect == "Sharpen":
                current_image = current_image.filter(ImageFilter.SHARPEN)
            elif selected_effect == "Contour":
                current_image = current_image.filter(ImageFilter.CONTOUR)
            elif selected_effect == "Emboss":
                current_image = current_image.filter(ImageFilter.EMBOSS)
            elif selected_effect == "Edge Enhance":
                current_image = current_image.filter(ImageFilter.EDGE_ENHANCE_MORE)
            # "None" does nothing to current_image

            # 2. Apply rotation (if angle is not 0)
            if rotation_angle != 0:
                # PIL rotates counter-clockwise. 'expand=True' makes sure the whole rotated image fits.
                current_image = current_image.rotate(rotation_angle, expand=True)

            # 3. Apply flips
            if flip_horizontal:
                current_image = ImageOps.mirror(current_image)
            if flip_vertical:
                current_image = ImageOps.flip(current_image)

            st.session_state.processed_pil_image = current_image
    
    if st.session_state.processed_pil_image and st.session_state.processed_pil_image != st.session_state.original_pil_image:
        st.sidebar.subheader("💾 Download Processed Image")
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        # Determine format based on original, or default to PNG
        original_format = st.session_state.original_pil_image.format if st.session_state.original_pil_image.format else 'PNG'

        # Pillow needs format for saving unless it's PNG which can be inferred from extension sometimes
        # For explicit control:
        save_format = original_format
        if save_format == 'JPEG': # Ensure quality for JPEGs if needed
             st.session_state.processed_pil_image.save(img_byte_arr, format=save_format, quality=95)
        else:
             st.session_state.processed_pil_image.save(img_byte_arr, format=save_format)

        img_byte_arr = img_byte_arr.getvalue()

        # Get original filename and append _processed
        try:
            original_filename = st.session_state.last_uploaded_filename.split('.')[0]
            original_extension = st.session_state.last_uploaded_filename.split('.')[-1]
            download_filename = f"{original_filename}_processed.{original_extension.lower()}"
        except: # Fallback if filename parsing fails
            download_filename = f"processed_image.{save_format.lower()}"


        st.sidebar.download_button(
            label="Download Image",
            data=img_byte_arr,
            file_name=download_filename,
            mime=f"image/{save_format.lower()}" # e.g., image/png or image/jpeg
        )

else:
    st.info("☝️ Upload an image using the sidebar to get started!")