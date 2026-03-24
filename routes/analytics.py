import matplotlib
matplotlib.use('Agg')

from flask import Blueprint, send_file
import numpy as np
import matplotlib.pyplot as plt
import io

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/qkd/entropy_stats')
def entropy_stats():
    # סימולציה של התפלגות ביטים (0 לעומת 1)
    labels = ['Bit 0', 'Bit 1']
    counts = [np.random.randint(450, 550), np.random.randint(450, 550)]
    
    # חישוב אנטרופיה (Shannon Entropy)
    total = sum(counts)
    p0 = counts[0] / total
    p1 = counts[1] / total
    entropy = - (p0 * np.log2(p0) + p1 * np.log2(p1))
    
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor('#0d1117')

    # גרף 1: התפלגות ביטים
    bars = ax1.bar(labels, counts, color=['#1f6feb', '#238636'], alpha=0.8)
    ax1.set_title("Bit Distribution (Randomness Check)", color='#c9d1d9', fontweight='bold')
    ax1.set_facecolor('#161b22')
    ax1.set_ylim(0, 700)
    
    # גרף 2: מד האנטרופיה
    ax2.set_facecolor('#161b22')
    circle = plt.Circle((0.5, 0.5), 0.4, color='#30363d', fill=False, lw=10)
    ax2.add_artist(circle)
    
    # ציור "מחוג" לפי האנטרופיה
    color = '#39d353' if entropy > 0.99 else '#e3b341'
    ax2.text(0.5, 0.5, f"{entropy:.4f}\nBits/Bit", ha='center', va='center', 
             fontsize=24, fontweight='bold', color=color)
    ax2.set_title("Shannon Entropy Score", color='#c9d1d9', fontweight='bold')
    ax2.axis('off')

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor='#0d1117')
    buf.seek(0)
    plt.close(fig)
    
    return send_file(buf, mimetype='image/png')