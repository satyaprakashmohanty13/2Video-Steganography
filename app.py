import streamlit as st
import os
import tempfile
from encode import encode_process
from decode import decode_process

def save_uploaded_file(uploaded_file):
    """Saves uploaded file to a temporary file and returns the path."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

st.set_page_config(page_title="Video Steganography", layout="wide")
st.title("Video Steganography Tool")
st.write("Hide secret messages within video files using AES or RSA encryption.")

# Generate RSA Keys button
if st.button("Generate RSA Keys"):
    try:
        # Assuming rsagen.py is in the same directory and works as a script.
        # This is a simplified way to call it. A better approach would be to refactor rsagen.py into a function.
        import rsagen
        st.success("Successfully generated RSA keys. Check the `keys` directory.")
    except Exception as e:
        st.error(f"Error generating RSA keys: {e}")


tab1, tab2 = st.tabs(["🔒 Encode", "🔓 Decode"])

with tab1:
    st.header("Encode a Message into a Video")

    col1, col2 = st.columns(2)
    with col1:
        uploaded_video = st.file_uploader("1. Upload a Video", type=["mp4", "mov", "avi"])
        message = st.text_area("2. Enter the message to hide")
        encryption_style = st.radio("3. Choose Encryption Style", ("AES", "RSA"))

    with col2:
        aes_key = st.text_input("AES Key (if using AES)", type="password")
        public_key_file = st.file_uploader("RSA Public Key (for RSA or to encrypt AES key)")
        frame_storage_image = st.file_uploader("Optional: Image to Hide Frame Numbers In")

    if st.button("Encode Video"):
        if not uploaded_video or not message:
            st.warning("Please provide a video and a message to encode.")
        else:
            with st.spinner("Encoding video... This may take a while."):
                video_path = save_uploaded_file(uploaded_video)
                key_path = save_uploaded_file(public_key_file) if public_key_file else None
                frame_image_path = save_uploaded_file(frame_storage_image) if frame_storage_image else None

                try:
                    result = encode_process(
                        video_path,
                        message,
                        encryption_style,
                        key=aes_key if aes_key else None,
                        key_path=key_path,
                        frame_storage_image=frame_image_path
                    )

                    st.success("Video encoded successfully!")

                    if 'video' in result and os.path.exists(result['video']):
                        with open(result['video'], "rb") as f:
                            st.download_button("Download Encoded Video", f, file_name="encoded_video.mov")

                    if 'image' in result and os.path.exists(result['image']):
                         with open(result['image'], "rb") as f:
                            st.download_button("Download Image with Frame #s", f, file_name="image-enc.png")

                    if 'encrypted_aes_key' in result:
                        st.info(f"Encrypted AES Key (share with receiver): `{result['encrypted_aes_key']}`")

                except Exception as e:
                    st.error(f"An error occurred during encoding: {e}")
                finally:
                    # Clean up temporary files
                    if video_path and os.path.exists(video_path): os.remove(video_path)
                    if key_path and os.path.exists(key_path): os.remove(key_path)
                    if frame_image_path and os.path.exists(frame_image_path): os.remove(frame_image_path)

with tab2:
    st.header("Decode a Message from a Video")

    col3, col4 = st.columns(2)
    with col3:
        encoded_video_file = st.file_uploader("1. Upload the Encoded Video", type=["mp4", "mov", "avi"])
        decryption_style = st.radio("2. Choose Decryption Style", ("AES", "RSA"))

        frame_source = st.radio("3. How are you providing frame numbers?", ("From an image", "Manually"))

    with col4:
        decode_aes_key = st.text_input("AES Key (if using AES)", type="password", key="decode_aes")
        private_key_file = st.file_uploader("RSA Private Key (for RSA decryption)")

        if frame_source == "From an image":
            encoded_image_file = st.file_uploader("Image with Hidden Frame Numbers")
            manual_frames_input = None
        else:
            manual_frames_input = st.text_input("Comma-separated frame numbers (e.g., 10,20,30)")
            encoded_image_file = None

    if st.button("Decode Video"):
        if not encoded_video_file:
            st.warning("Please upload the encoded video.")
        else:
            with st.spinner("Decoding video..."):
                video_path = save_uploaded_file(encoded_video_file)
                image_path = save_uploaded_file(encoded_image_file) if encoded_image_file else None
                rsa_key_path = save_uploaded_file(private_key_file) if private_key_file else None

                try:
                    decrypted_message = decode_process(
                        encoded_video_path=video_path,
                        decryption_style=decryption_style,
                        encoded_image_path=image_path,
                        frames_input=manual_frames_input,
                        key=decode_aes_key if decode_aes_key else None,
                        rsa_key_path=rsa_key_path
                    )
                    st.success("Successfully decoded the message:")
                    st.code(decrypted_message, language="")
                except Exception as e:
                    st.error(f"An error occurred during decoding: {e}")
                finally:
                     if video_path and os.path.exists(video_path): os.remove(video_path)
                     if image_path and os.path.exists(image_path): os.remove(image_path)
                     if rsa_key_path and os.path.exists(rsa_key_path): os.remove(rsa_key_path)
