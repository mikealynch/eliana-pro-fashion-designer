import os
import streamlit as st
import replicate
from dotenv import load_dotenv
import webcolors

# Load environment variables
load_dotenv()

# Set up Replicate API client with the token from environment variables
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

if not REPLICATE_API_TOKEN:
    st.error("Missing Replicate API token. Please set the 'REPLICATE_API_TOKEN' environment variable.")
else:
    client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# Streamlit UI
st.title("Eliana's Pro Fashion Designer")
st.write("Design your dream clothing with AI-powered fashion design.")

# Function to convert hex color to approximate text name
def hex_to_name(hex_color):
    try:
        # Get the closest CSS3 color name
        color_name = webcolors.hex_to_name(hex_color, spec='css3')
    except ValueError:
        # If no exact match is found, use the hex value as a fallback
        color_name = f"hex color {hex_color}"
    return color_name

# User input for attributes
clothing_type = st.selectbox(
    "Choose the type of clothing:",
    ["Dress", "Shoes", "Shirt", "Skirt"]
)

fabric_type = st.text_input("Enter the fabric type (e.g., cotton, silk, denim):")
fabric_color_hex = st.color_picker("Pick a fabric color:")
fabric_color_name = hex_to_name(fabric_color_hex)  # Convert hex to name
thread_type = st.text_input("Enter the thread type (e.g., polyester, cotton):")
additional_details = st.text_area("Add additional details (e.g., floral pattern, stripes):")


def generate_image(prompt):
    """
    Generate an image using Replicate's Stable Diffusion.
    """
    try:
        # Run the model on Replicate
        output = replicate.run(
            "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
            input={
                "width": 512,
                "height": 512,
                "prompt": prompt,
                "scheduler": "K_EULER",
                "num_outputs": 1,
                "guidance_scale": 15,
                "num_inference_steps": 100,
            }
        )
        # Debugging: Inspect output format
        print(f"Output type: {type(output)}")
        print(f"Output content: {output}")

        # Check if output is a list containing FileOutput objects
        if isinstance(output, list) and all(isinstance(o, replicate.helpers.FileOutput) for o in output):
            # Save the file locally
            file_path = "output_image.png"
            with open(file_path, "wb") as f:
                f.write(output[0].read())
            return file_path  # Return the local file path
        else:
            raise Exception(f"Unexpected output format: {output}")
    except replicate.exceptions.ReplicateException as re:
        raise Exception(f"Replicate API Error: {re}")
    except Exception as e:
        raise Exception(f"General Error: {e}")


if st.button("Generate Design"):
    if not fabric_type or not thread_type:
        st.warning("Please fill out all required fields.")
    else:
        # Enhanced prompt to emphasize the fabric color
        prompt = (    
                       f"A highly detailed and vibrant {fabric_color_name} {clothing_type} made of {fabric_type}, worn by a woman, child-friendly, elegant and playful, professional fashion photoshoot, intricate fabric texture, high-quality studio lighting."
        )
        
        st.write("Generating your design...")
        # Generate image with Replicate's Stable Diffusion
        try:
            image_path = generate_image(prompt)
            # Display the generated image
            #st.image(image_path, caption="Your AI-generated design")
            st.image(image_path, caption=prompt)
            
            # Provide a download button
            with open(image_path, "rb") as img_file:
                st.download_button(
                    label="Download Image",
                    data=img_file,
                    file_name="fashion_design.png",
                    mime="image/png",
                )
        except Exception as e:
            st.error(f"An error occurred: {e}")
