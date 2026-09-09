import os
import sys
import socket
import qrcode
from PIL import Image, ImageDraw

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def generate_dd_qr(url=None):
    if not url:
        ip = get_local_ip()
        url = f"http://{ip}:8000"
    
    print(f"Generating Single Master QR Code for Dosth Dhaba: {url}")

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="#121212", back_color="#ffffff").convert('RGB')

    card_w = 460
    card_h = 580
    card = Image.new("RGB", (card_w, card_h), "#121212")
    draw = ImageDraw.Draw(card)

    draw.rectangle([10, 10, card_w - 10, card_h - 10], outline="#f39c12", width=3)
    draw.rectangle([15, 15, card_w - 15, card_h - 15], outline="#f1c40f", width=1)

    qr_resized = qr_img.resize((340, 340))
    card.paste(qr_resized, (60, 95))

    draw.rectangle([40, 22, card_w - 40, 56], fill="#f39c12")
    draw.text((card_w // 2, 39), "DOSTH DHABA", fill="#000000", anchor="mm")
    draw.text((card_w // 2, 75), "DIGITAL MENU & ORDERING", fill="#f1c40f", anchor="mm")

    draw.text((card_w // 2, 470), "SCAN TO ORDER FOOD", fill="#ffffff", anchor="mm")
    draw.text((card_w // 2, 500), "Select your Hut / Table after scanning", fill="#f39c12", anchor="mm")
    draw.text((card_w // 2, 530), "100% Halal * WhatsApp Digital Bill", fill="#888888", anchor="mm")

    output_dir = os.path.dirname(os.path.abspath(__file__))
    qr_path = os.path.join(output_dir, "dd_ordering_qr.png")
    card.save(qr_path)
    print(f"Saved Master Branded QR code to: {qr_path}")

    # Also save clean plain QR code for small table stickers
    plain_qr_path = os.path.join(output_dir, "restaurant_qr.png")
    qr_img.save(plain_qr_path)
    print(f"Saved Clean Table QR code to: {plain_qr_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("Tip: You can pass your public URL as argument:")
        print("  python generate_qr.py https://your-public-url.onrender.com\n")
        user_url = input("Enter Public URL (or press Enter for auto): ").strip()
        url = user_url if user_url else None
    generate_dd_qr(url)
