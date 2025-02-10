import streamlit as st
import requests
import imageio
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Set up Tenor API key (get your own key from https://tenor.com/gifapi/documentation)
TENOR_API_KEY=st.secrets["TENOR_API_KEY"]


# Function to fetch GIF from Tenor
def fetch_gif(query):
    url = f"https://tenor.googleapis.com/v2/search?q={query}&key={TENOR_API_KEY}&limit=1&media_filter=minimal"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results'][0]['media_formats']['gif']['url']
    return None

import requests
import imageio
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def add_text_to_gif(gif_url, text, position, font_size, color):
    response = requests.get(gif_url)
    gif_bytes = BytesIO(response.content)
    gif = Image.open(gif_bytes)

    frames = []
    try:
        while True:
            frame = gif.convert("RGBA")  # Keep high quality
            
            # Create transparent layer for text
            text_layer = Image.new("RGBA", frame.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(text_layer)

            font_path = "fonts/Roboto-Italic-VariableFont_wdth,wght.ttf"  # Mets le chemin correct
            font = ImageFont.truetype(font_path, font_size)


            # Get text size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            padding = 10

            # Define text positions
            positions = {
                "Top Left": (padding, padding),
                "Top Right": (frame.width - text_width - padding, padding),
                "Bottom Left": (padding, frame.height - text_height - padding),
                "Bottom Right": (frame.width - text_width - padding, frame.height - text_height - padding),
            }
            text_position = positions.get(position, (50, 50))

            # Add text to transparent layer
            draw.text(text_position, text, fill=color, font=font)

            # Merge text layer with the frame
            frame = Image.alpha_composite(frame, text_layer)

            # Convert back to RGB for imageio (GIFs don't support RGBA)
            frame = frame.convert("RGB")
            frames.append(frame)

            gif.seek(gif.tell() + 1)
    except EOFError:
        pass

    # Save GIF using imageio (better compression & quality)
    output_gif = BytesIO()
    imageio.mimsave(output_gif, frames, format="GIF", duration=gif.info.get("duration", 100) / 500, loop=0)
    output_gif.seek(0)
    return output_gif



# Streamlit UI
st.title("GIF Generator with Custom Text Overlay 🎨")

# User input for GIF search
query = st.text_input("Enter a GIF search term (e.g., 'funny cat')", "Goku Vegeta Fusion")

# User input for overlay text
overlay_text = st.text_input("Enter text to overlay", "Goku Analyst + Vegeta Engineer  = Gogeta Scientist!!")

# Position selection
position = st.selectbox("Choose text position", ["Top Left", "Top Right", "Bottom Left", "Bottom Right"])

# Font size selection
font_size = st.slider("Font Size", min_value=10, max_value=80, value=18)

# Color selection
text_color = st.color_picker("Pick a text color", "#000000")

# Generate GIF button
if st.button("Generate GIF"):
    st.write("Fetching GIF...")
    gif_url = fetch_gif(query)

    if gif_url:
        st.image(gif_url, caption="Original GIF")

        # Process GIF with text overlay
        st.write("Processing GIF with custom text...")
        modified_gif = add_text_to_gif(gif_url, overlay_text, position, font_size, text_color)

        # Display modified GIF
        st.image(modified_gif, caption="Modified GIF")
        st.download_button("Download Modified GIF", modified_gif, file_name="custom_gif.gif", mime="image/gif")
    else:
        st.error("Failed to fetch GIF. Try another search term.")
