from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image
from io import BytesIO
import os
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types
import tempfile
import shutil
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# --- Gemini prompt enhancement ---
def enhance_prompt_gemini(prompt):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemini-2.0-flash-001"
    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=f"""You are an expert prompt engineer specializing in generating high-resolution, visually compelling posters using the Imagen 4 model. Your objective is to meticulously translate user-provided poster concepts into detailed, structured prompts that maximize visual quality, avoid distortions, and eliminate spelling errors or extraneous text.
For each user prompt provided, you will generate a comprehensive description that adheres to the following criteria:
Title/Theme: Clearly and concisely state the primary message or title of the poster. Ensure it is impactful and easily understood.
Visual Style: Define a specific and coherent artistic style. Use descriptive terms such as:
Modern: Clean lines, geometric shapes, often minimalist.
Minimalist: Sparse design, focused on essential elements, ample negative space.
Futuristic: Sleek designs, metallic textures, glowing elements, advanced technology motifs.
Vibrant: Bold colors, dynamic compositions, energetic feel.
Retro/Vintage: Emulating specific historical design periods (e.g., Art Deco, mid-century modern).
Artistic: Characterized by specific artistic movements (e.g., Surrealism, Impressionism, Abstract Expressionism).
Illustrative: Dominated by custom artwork or detailed drawings.
Photorealistic: Emphasizing lifelike imagery.
Typographic: Primarily driven by creative and impactful typography.
Clean & Professional: Organized, balanced, and sophisticated.
Color Scheme: Specify a limited and harmonious color palette (e.g., a primary color, a secondary accent color, and a neutral). Crucially, do not provide HEX codes or specific color values, but rather descriptive names (e.g., "deep ocean blue and bright coral," "emerald green and brushed gold," "soft pastels like blush pink and sky blue"). The palette should support the theme and visual style.
Typography: Describe the desired typography for the main title and any prominent text. Focus on legibility and impact for large-scale display:
Font Type: Specify font categories (e.g., sans-serif, serif, script, display).
Weight/Style: Mention bold, heavy, condensed, italicized.
Placement: Indicate where the primary text should be positioned for maximum visibility.
Hierarchy: If applicable, suggest how different text elements should be visually prioritized.
Graphic Elements: Detail specific illustrative components, icons, motifs, or imagery that directly support the theme. Be precise in describing their style and function within the poster. Examples:
Illustrations: "stylized vector illustrations of orbiting planets," "hand-drawn botanical elements," "abstract geometric patterns."
Icons: "minimalist icons representing data and connectivity," "vintage-style emblems."
Motifs: "subtle circuitry patterns," "flowing water textures," "star constellations."
Background: Define the background to ensure it complements, rather than competes with, the main content. Options include:
Gradients: Specify the direction and color transition (e.g., "a smooth radial gradient from dark navy to light cyan").
Abstract Textures: Describe the nature of the texture (e.g., "subtle paper texture," "soft bokeh effect," "fine noise grain").
Solid Color: A simple, unobtrusive solid color.
Subtle Pattern: A very faint, repeating design that doesn't draw attention.
Crucially, the background should never be distracting or contain discernible text.
Audience & Purpose: Clearly state the intended audience and the overall purpose of the poster to inform the tone and visual communication.
Audience Examples: "young adults," "tech professionals," "families," "academic community," "general public."
Purpose Examples: "informational event announcement," "promotional campaign," "celebratory greeting," "educational awareness."
Tone Examples: "energetic and engaging," "formal and authoritative," "friendly and approachable," "sophisticated and inspiring."
Clarity & Attention: Emphasize that the final design must be highly readable and attention-grabbing from a distance, with a clear visual hierarchy and no overcrowding.
Important Constraints for Imagen 4:
No Distortions: Ensure the prompt guides Imagen 4 to produce geometrically sound and proportionally accurate visuals.
No Spelling Mistakes: The generated prompt will be free of typos.
No Unwanted Text: The generated poster should contain only the specified text and no unintended or extraneous words.
Focus on Visuals: The prompt should prioritize visual elements and descriptions over lengthy prose.
all indian motifs should be incorporated into the design, including traditional patterns and symbols.

                              
Output Format:
Your output should be a single, coherent prompt string ready for direct input into Imagen 4.
                              

Example of desired output based on the provided example:
                              
"Create a high-resolution poster for an 'Annual Tech Fest 2025'. The visual style should be clean and modern, utilizing a bold color palette of electric blue and crisp white. The main title, 'Annual Tech Fest 2025', should be rendered in a large, bold sans-serif font, prominently placed at the top. The background should feature abstract, subtle tech-themed geometric patterns that do not distract from the main content. Incorporate a designated empty space in the top-left corner for a college logo placement. The overall tone should be energetic and appealing to young students, suitable for a college campus display. Prioritize exceptional readability and immediate visual impact."
Now, this is the user prompt:
                              
{prompt}

""")]
        )
    ]
    generate_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(),
        response_mime_type="text/plain"
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_config
    ):
        response_text += chunk.text
    return response_text

# --- Imagen image generation ---
def generate_poster(prompt, aspect_ratio):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    result = client.models.generate_images(
        model="models/imagen-4.0-generate-preview-06-06",
        prompt=prompt,
        config=dict(
            number_of_images=3,
            output_mime_type="image/jpeg",
            person_generation="ALLOW_ADULT",
            aspect_ratio=aspect_ratio,
        ),
    )

    if not result.generated_images:
        return []

    images = [Image.open(BytesIO(img.image.image_bytes)).convert("RGBA") for img in result.generated_images]
    return images

# --- Overlay logo on poster ---
def overlay_logo(poster, logo, position, scale):
    logo = logo.convert("RGBA")
    logo_width = int(poster.width * scale)
    logo = logo.resize((logo_width, int(logo.height * (logo_width / logo.width))))
    x, y = position
    poster = poster.copy()
    poster.paste(logo, (int(x), int(y)), logo)
    return poster

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enhance-prompt', methods=['POST'])
def enhance_prompt():
    try:
        data = request.get_json()
        user_prompt = data.get('prompt', '')
        
        if not user_prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        enhanced_prompt = enhance_prompt_gemini(user_prompt)
        return jsonify({'enhanced_prompt': enhanced_prompt})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-poster', methods=['POST'])
def generate_poster_route():
    try:
        # Accept both JSON and multipart/form-data
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            prompt = request.form.get('prompt', '')
            aspect_ratio = request.form.get('aspect_ratio', '9:16')
            logo_file = request.files.get('logo')
        else:
            data = request.get_json()
            prompt = data.get('prompt', '')
            aspect_ratio = data.get('aspect_ratio', '9:16')
            logo_file = None

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        posters = generate_poster(prompt, aspect_ratio)

        if not posters:
            return jsonify({'error': 'Failed to generate posters'}), 500

        # If logo is provided, overlay it on each poster
        if logo_file:
            logo_img = Image.open(logo_file.stream).convert('RGBA')
            # Default: scale logo to 20% of poster width, place at (30, 30)
            scale = 0.2
            position = (30, 30)
            posters = [overlay_logo(poster, logo_img, position, scale) for poster in posters]

        # Convert images to base64 for JSON response
        poster_data = []
        for i, poster in enumerate(posters):
            buffered = BytesIO()
            poster.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            poster_data.append({
                'id': f'poster_{i}',
                'image': img_str,
                'width': poster.width,
                'height': poster.height
            })

        return jsonify({'posters': poster_data})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/overlay-logo', methods=['POST'])
def overlay_logo_route():
    try:
        # This would handle logo overlay functionality
        # Implementation depends on how you want to handle the logo upload and positioning
        return jsonify({'message': 'Not implemented'}), 501
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)