import matplotlib
matplotlib.use('Agg')

from flask import Blueprint, request, send_file
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import hashlib
import io

privacy_bp = Blueprint('privacy', __name__)

@privacy_bp.route('/qkd/privacy')
def visualize_privacy():
    # כמה אחוז מהמפתח איב הצליחה לנחש (מהסליידר ב-UI)
    eve_knowledge = int(request.args.get('knowledge', 25))
    
    num_bits = 16
    final_bits = 8
    
    # ייצור מפתח מקורי "מתוקן" אקראי
    original_key = np.random.randint(2, size=num_bits)
    
    # בחירת ביטים שאיב "יודעת"
    num_compromised = int((eve_knowledge / 100.0) * num_bits)
    compromised_indices = np.random.choice(num_bits, num_compromised, replace=False)
    
    # הפעלת פונקציית Hash (גיבוב) אמיתית!
    key_str = ''.join(map(str, original_key))
    hash_hex = hashlib.sha256(key_str.encode()).hexdigest()
    # לוקחים את ה-8 ביטים הראשונים מההאש
    secure_key = [int(c, 16) % 2 for c in hash_hex[:final_bits]]
    
    # --- תחילת ציור הגרף ---
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(12, 6))
    fig.patch.set_facecolor('#0d1117')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#0d1117')
    ax.axis('off')
    
    bit_colors = {0: '#1f6feb', 1: '#238636'}
    
    # 1. ציור המפתח המקורי
    ax.text(num_bits/2 - 0.5, 2.5, "1. Reconciled Key (16 bits)", ha='center', color='#c9d1d9', fontsize=12, fontweight='bold')
    if eve_knowledge > 0:
        ax.text(num_bits/2 - 0.5, 2.1, f"⚠️ Eve knows ~{eve_knowledge}% of these bits (Highlighted Red)", ha='center', color='#f85149', fontsize=10)
    
    for i in range(num_bits):
        bit = original_key[i]
        edge_color = '#f85149' if i in compromised_indices else 'none'
        line_width = 3 if i in compromised_indices else 0
        rect = patches.Rectangle((i-0.4, 1.2), 0.8, 0.8, facecolor=bit_colors[bit], edgecolor=edge_color, linewidth=line_width, alpha=0.8)
        ax.add_patch(rect)
        ax.text(i, 1.6, str(bit), ha='center', va='center', fontsize=14, fontweight='bold', color='white')

    # 2. פונקציית הגיבוב (Hash)
    box = patches.FancyBboxPatch((num_bits/4 - 0.5, 0.2), num_bits/2, 0.6, boxstyle="round,pad=0.1", fc="#21262d", ec="#58a6ff", lw=2)
    ax.add_patch(box)
    ax.text(num_bits/2 - 0.5, 0.5, "⬇️ SHA-256 Cryptographic Hash ⬇️\n(Key Compression & Mixing)", ha='center', va='center', color='#58a6ff', fontsize=12, fontweight='bold')

    # 3. ציור המפתח הסופי המאובטח
    offset = (num_bits - final_bits) / 2
    ax.text(num_bits/2 - 0.5, -0.2, "2. Final Secure Key (8 bits)", ha='center', color='#39d353', fontsize=12, fontweight='bold')
    ax.text(num_bits/2 - 0.5, -0.6, "✅ Eve's knowledge reduced to 0.00%", ha='center', color='#39d353', fontsize=10)
    
    for i in range(final_bits):
        bit = secure_key[i]
        pos_x = i + offset
        rect = patches.Rectangle((pos_x-0.4, -1.6), 0.8, 0.8, facecolor=bit_colors[bit], edgecolor='#39d353', linewidth=2, alpha=0.9)
        ax.add_patch(rect)
        ax.text(pos_x, -1.2, str(bit), ha='center', va='center', fontsize=14, fontweight='bold', color='white')

    ax.set_xlim(-1, num_bits)
    ax.set_ylim(-2, 3)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    
    return send_file(buf, mimetype='image/png')