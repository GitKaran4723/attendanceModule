"""
Icon Generator for PWA
This script generates placeholder icons for the PWA.
You can replace these with your own custom icons later.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """
    Create a simple icon with the app initial 'A' for Attendance
    """
    # Create image with purple background (Material Design primary color)
    img = Image.new('RGB', (size, size), color='#6200ea')
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fallback to default if not available
    try:
        # Calculate font size based on icon size
        font_size = int(size * 0.6)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Draw the letter 'A' in white
    text = "A"
    
    # Get text bounding box to center it
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position to center the text
    x = (size - text_width) / 2
    y = (size - text_height) / 2 - bbox[1]
    
    draw.text((x, y), text, fill='white', font=font)
    
    # Save the image
    img.save(output_path, 'PNG')
    print(f"Created icon: {output_path}")

def main():
    """
    Generate all required icon sizes
    """
    # Create icons directory if it doesn't exist
    icons_dir = 'static/icons'
    os.makedirs(icons_dir, exist_ok=True)
    
    # Icon sizes required by the manifest
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    print("Generating PWA icons...")
    
    for size in sizes:
        output_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
        create_icon(size, output_path)
    
    print("\n✅ All icons generated successfully!")
    print("📱 You can now install the PWA on your mobile device.")
    print("💡 Tip: Replace these placeholder icons with your custom design for a professional look.")

if __name__ == '__main__':
    main()
