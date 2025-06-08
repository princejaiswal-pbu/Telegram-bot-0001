"""
QR Code generation utilities
"""

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SquareGradiantColorMask
from PIL import Image, ImageDraw, ImageFont
import os

def generate_upi_qr(upi_url: str, filename: str = "payment_qr.png") -> bool:
    """Generate a stylized UPI QR code"""
    
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add UPI URL data
        qr.add_data(upi_url)
        qr.make(fit=True)
        
        # Create stylized QR code with cyberpunk colors
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=SquareGradiantColorMask(
                back_color=(10, 14, 39),      # Dark blue background
                center_color=(0, 212, 255),    # Neon blue center
                edge_color=(255, 0, 110)       # Neon pink edges
            )
        )
        
        # Create a larger canvas with branding
        canvas_size = (600, 700)
        canvas = Image.new('RGB', canvas_size, (10, 14, 39))  # Dark background
        
        # Resize QR code
        qr_size = 400
        img = img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        
        # Calculate position to center QR code
        qr_x = (canvas_size[0] - qr_size) // 2
        qr_y = 100
        
        # Paste QR code onto canvas
        canvas.paste(img, (qr_x, qr_y))
        
        # Add title and instructions
        draw = ImageDraw.Draw(canvas)
        
        try:
            # Try to use a system font
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Title
        title_text = "🔐 QUICK ESCROW"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (canvas_size[0] - title_width) // 2
        draw.text((title_x, 30), title_text, fill=(0, 212, 255), font=title_font)
        
        # Subtitle
        subtitle_text = "Scan to Pay with UPI"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (canvas_size[0] - subtitle_width) // 2
        draw.text((subtitle_x, 520), subtitle_text, fill=(255, 255, 255), font=subtitle_font)
        
        # Security badge
        security_text = "🛡️ Secured by Quick Escrow Bot"
        security_bbox = draw.textbbox((0, 0), security_text, font=subtitle_font)
        security_width = security_bbox[2] - security_bbox[0]
        security_x = (canvas_size[0] - security_width) // 2
        draw.text((security_x, 550), security_text, fill=(0, 255, 136), font=subtitle_font)
        
        # Instructions
        instruction_text = "⚡ Any UPI app • 💎 Instant • 🔥 Secure"
        instruction_bbox = draw.textbbox((0, 0), instruction_text, font=subtitle_font)
        instruction_width = instruction_bbox[2] - instruction_bbox[0]
        instruction_x = (canvas_size[0] - instruction_width) // 2
        draw.text((instruction_x, 580), instruction_text, fill=(255, 215, 10), font=subtitle_font)
        
        # Add decorative elements
        # Corner brackets for cyberpunk effect
        bracket_color = (0, 212, 255)
        bracket_width = 3
        bracket_length = 30
        
        # Top-left bracket
        draw.line([(qr_x-20, qr_y-20), (qr_x-20+bracket_length, qr_y-20)], fill=bracket_color, width=bracket_width)
        draw.line([(qr_x-20, qr_y-20), (qr_x-20, qr_y-20+bracket_length)], fill=bracket_color, width=bracket_width)
        
        # Top-right bracket
        draw.line([(qr_x+qr_size+20-bracket_length, qr_y-20), (qr_x+qr_size+20, qr_y-20)], fill=bracket_color, width=bracket_width)
        draw.line([(qr_x+qr_size+20, qr_y-20), (qr_x+qr_size+20, qr_y-20+bracket_length)], fill=bracket_color, width=bracket_width)
        
        # Bottom-left bracket
        draw.line([(qr_x-20, qr_y+qr_size+20-bracket_length), (qr_x-20, qr_y+qr_size+20)], fill=bracket_color, width=bracket_width)
        draw.line([(qr_x-20, qr_y+qr_size+20), (qr_x-20+bracket_length, qr_y+qr_size+20)], fill=bracket_color, width=bracket_width)
        
        # Bottom-right bracket
        draw.line([(qr_x+qr_size+20-bracket_length, qr_y+qr_size+20), (qr_x+qr_size+20, qr_y+qr_size+20)], fill=bracket_color, width=bracket_width)
        draw.line([(qr_x+qr_size+20, qr_y+qr_size+20-bracket_length), (qr_x+qr_size+20, qr_y+qr_size+20)], fill=bracket_color, width=bracket_width)
        
        # Save the final image
        canvas.save(filename, "PNG", quality=95)
        
        return True
        
    except Exception as e:
        print(f"Error generating QR code: {e}")
        
        # Fallback to simple QR code
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(upi_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(filename)
            
            return True
        except:
            return False

def generate_simple_qr(data: str, filename: str = "simple_qr.png") -> bool:
    """Generate a simple QR code as fallback"""
    
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        
        return True
        
    except Exception as e:
        print(f"Error generating simple QR code: {e}")
        return False
