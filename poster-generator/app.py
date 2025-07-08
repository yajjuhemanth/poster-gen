from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
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
import re
import json
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")  # Needed for session management

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

# --- Persistent history ---
HISTORY_FILE = 'generation_history.json'
generation_history = []

def load_history():
    global generation_history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                generation_history = json.load(f)
            except Exception:
                generation_history = []
    else:
        generation_history = []

def save_history():
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(generation_history, f, ensure_ascii=False, indent=2)

# Load history at startup
load_history()

# --- Routes ---
@app.route('/', methods=['GET'])
def landing():
    return render_template('landing.html')

@app.route('/history')
def history():
    # Sort by most recent first
    sorted_history = sorted(generation_history, key=lambda x: x.get('timestamp', ''), reverse=True)
    return render_template('history.html', history=sorted_history)

@app.route('/enhance', methods=['POST'])
def enhance():
    prompt = request.form.get('prompt', '').strip()
    aspect_ratio = request.form.get('aspect_ratio', '9:16')
    if not prompt:
        flash('Prompt is required.')
        return redirect(url_for('landing'))
    # Call Gemini for enhanced prompt
    enhanced_prompt = enhance_prompt_gemini(prompt)
    # Call Gemini to suggest objects and color combinations
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        model = "gemini-2.0-flash-001"
        # Suggest objects
        objects_prompt = f"""
Given the following enhanced poster prompt, suggest a list of 5-8 distinct visual objects, motifs, or elements that would be visually compelling and relevant for the poster. Return only a JSON array of short object names or phrases, nothing else.\n\nPrompt:\n{enhanced_prompt}
"""
        color_prompt = f"""
Given the following enhanced poster prompt, suggest 3-5 harmonious color combinations (each as a short descriptive phrase, e.g., 'emerald green and brushed gold', 'deep ocean blue and bright coral'). Return only a JSON array of color combination strings, nothing else.\n\nPrompt:\n{enhanced_prompt}
"""
        # Get objects
        objects_contents = [types.Content(role="user", parts=[types.Part(text=objects_prompt)])]
        color_contents = [types.Content(role="user", parts=[types.Part(text=color_prompt)])]
        generate_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(),
            response_mime_type="text/plain"
        )
        # Objects
        objects_response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=objects_contents,
            config=generate_config
        ):
            if hasattr(chunk, 'text') and chunk.text:
                objects_response += chunk.text
        import json as _json
        try:
            objects = _json.loads(objects_response)
            if not isinstance(objects, list):
                objects = [str(objects)]
        except Exception:
            objects = []
        # Colors
        colors_response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=color_contents,
            config=generate_config
        ):
            if hasattr(chunk, 'text') and chunk.text:
                colors_response += chunk.text
        try:
            color_combinations = _json.loads(colors_response)
            if not isinstance(color_combinations, list):
                color_combinations = [str(color_combinations)]
        except Exception:
            color_combinations = []
    except Exception:
        objects = []
        color_combinations = []
    return render_template('enhance.html', prompt=prompt, aspect_ratio=aspect_ratio, enhanced_prompt=enhanced_prompt, objects=objects, color_combinations=color_combinations)

@app.route('/generate', methods=['POST'])
def generate():
    enhanced_prompt = request.form.get('enhanced_prompt', '').strip()
    prompt = request.form.get('prompt', '').strip()
    aspect_ratio = request.form.get('aspect_ratio', '9:16')
    # Get selected objects and color combinations (may be empty lists)
    objects = request.form.getlist('objects[]')
    color_combinations = request.form.getlist('color_combinations[]')
    # Go to logo upload step, pass selected options forward if needed
    return render_template('step3_logo.html', enhanced_prompt=enhanced_prompt, prompt=prompt, aspect_ratio=aspect_ratio, objects=objects, color_combinations=color_combinations)

@app.route('/step4', methods=['POST'])
def step4():
    enhanced_prompt = request.form.get('enhanced_prompt', '').strip()
    prompt = request.form.get('prompt', '').strip()
    aspect_ratio = request.form.get('aspect_ratio', '9:16')
    logo_file = request.files.get('logo')
    logo_position = request.form.get('logo_position', 'top-left')
    # Generate posters
    posters = generate_poster(prompt, aspect_ratio)
    poster_data = []
    # Logo overlay logic
    def get_logo_xy(pos, poster, logo, scale=0.18):
        w, h = poster.width, poster.height
        lw = int(w * scale)
        lh = int(logo.height * (lw / logo.width))
        if pos == 'top-left':
            return (int(w*0.03), int(h*0.03))
        elif pos == 'top-right':
            return (w - lw - int(w*0.03), int(h*0.03))
        elif pos == 'bottom-left':
            return (int(w*0.03), h - lh - int(h*0.03))
        elif pos == 'bottom-right':
            return (w - lw - int(w*0.03), h - lh - int(h*0.03))
        elif pos == 'center':
            return ((w - lw)//2, (h - lh)//2)
        else:
            return (int(w*0.03), int(h*0.03))
    for i, poster in enumerate(posters):
        img = poster
        if logo_file and logo_file.filename:
            try:
                logo = Image.open(logo_file.stream).convert("RGBA")
                pos = get_logo_xy(logo_position, poster, logo)
                img = overlay_logo(poster, logo, pos, scale=0.18)
            except Exception:
                pass
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        poster_data.append({
            'id': f'poster_{i}',
            'image': img_str,
            'width': img.width,
            'height': img.height
        })
    # Save to history with timestamp
    generation_history.append({
        'prompt': prompt,
        'aspect_ratio': aspect_ratio,
        'posters': poster_data,
        'timestamp': datetime.now().isoformat()
    })
    save_history()
    return render_template('generate.html', posters=poster_data, prompt=prompt, aspect_ratio=aspect_ratio)

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
        else:
            data = request.get_json()
            prompt = data.get('prompt', '')
            aspect_ratio = data.get('aspect_ratio', '9:16')

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        posters = generate_poster(prompt, aspect_ratio)

        if not posters:
            return jsonify({'error': 'Failed to generate posters'}), 500

        # Do NOT overlay logo in backend. Only return generated posters.
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

        # Save to history with timestamp
        generation_history.append({
            'prompt': prompt,
            'aspect_ratio': aspect_ratio,
            'posters': poster_data,
            'timestamp': datetime.now().isoformat()
        })
        save_history()

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

@app.route('/regen-suggestions', methods=['POST'])
def regen_suggestions():
    try:
        data = request.get_json()
        enhanced_prompt = data.get('enhanced_prompt', '').strip()
        if not enhanced_prompt:
            return jsonify({'error': 'Enhanced prompt required'}), 400
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        model = "gemini-2.0-flash-001"
        # Suggest objects
        objects_prompt = f"""
Given the following enhanced poster prompt, suggest a list of 5-8 distinct visual objects, motifs, or elements that would be visually compelling and relevant for the poster. Return only a JSON array of short object names or phrases, nothing else.\n\nPrompt:\n{enhanced_prompt}
"""
        color_prompt = f"""
Given the following enhanced poster prompt, suggest 3-5 harmonious color combinations (each as a short descriptive phrase, e.g., 'emerald green and brushed gold', 'deep ocean blue and bright coral'). Return only a JSON array of color combination strings, nothing else.\n\nPrompt:\n{enhanced_prompt}
"""
        # Get objects
        objects_contents = [types.Content(role="user", parts=[types.Part(text=objects_prompt)])]
        color_contents = [types.Content(role="user", parts=[types.Part(text=color_prompt)])]
        generate_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(),
            response_mime_type="text/plain"
        )
        # Objects
        objects_response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=objects_contents,
            config=generate_config
        ):
            if hasattr(chunk, 'text') and chunk.text:
                objects_response += chunk.text
        import json as _json
        try:
            objects = _json.loads(objects_response)
            if not isinstance(objects, list):
                objects = [str(objects)]
        except Exception:
            objects = []
        # Colors
        colors_response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=color_contents,
            config=generate_config
        ):
            if hasattr(chunk, 'text') and chunk.text:
                colors_response += chunk.text
        try:
            color_combinations = _json.loads(colors_response)
            if not isinstance(color_combinations, list):
                color_combinations = [str(color_combinations)]
        except Exception:
            color_combinations = []
        return jsonify({'objects': objects, 'color_combinations': color_combinations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_key_features(enhanced_prompt):
    # Simple regex-based extraction for demo purposes
    features = {
        'title': '',
        'visual_style': '',
        'color_scheme': '',
        'typography': '',
        'graphic_elements': '',
        'background': '',
        'audience': '',
        'purpose': '',
        'tone': '',
    }
    # Try to extract each feature from the enhanced prompt
    for key in features:
        pattern = re.compile(rf'{key.replace("_", " ").title()}:\s*(.*?)(?:\.|$)', re.IGNORECASE)
        match = pattern.search(enhanced_prompt)
        if match:
            features[key] = match.group(1).strip()
    return features

@app.route('/extract-features', methods=['POST'])
def extract_features():
    try:
        data = request.get_json()
        enhanced_prompt = data.get('enhanced_prompt', '')
        if not enhanced_prompt:
            return jsonify({'error': 'Enhanced prompt required'}), 400
        features = extract_key_features(enhanced_prompt)
        return jsonify({'features': features})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)