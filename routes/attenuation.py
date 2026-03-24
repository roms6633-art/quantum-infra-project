import matplotlib
matplotlib.use('Agg')

from flask import Blueprint, request, send_file
import numpy as np
import matplotlib.pyplot as plt
import io

# הגדרת ה-Blueprint!
attenuation_bp = Blueprint('attenuation', __name__)

@attenuation_bp.route('/qkd/simulate_distance')
def simulate_distance():
    current_km = float(request.args.get('km', 0))
    distances = np.linspace(0, 150, 100)
    attenuation_coeff = 0.2  # 0.2 dB/km
    base_rate = 10000        
    
    rates = base_rate * (10 ** (-(attenuation_coeff * distances) / 10))
    current_rate = base_rate * (10 ** (-(attenuation_coeff * current_km) / 10))
    
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(10, 5))
    fig.patch.set_facecolor('#161b22')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#161b22')
    
    ax.plot(distances, rates, color='#58a6ff', linewidth=2, label='Theoretical Key Rate')
    ax.fill_between(distances, rates, color='#58a6ff', alpha=0.1)
    
    ax.scatter([current_km], [current_rate], color='#f85149', s=100, zorder=5, label=f'Current: {current_km} km')
    ax.vlines(x=current_km, ymin=0, ymax=current_rate, color='#f85149', linestyle='--', alpha=0.7)
    
    ax.set_title("QKD Performance vs. Fiber Distance (0.2 dB/km Attenuation)", color='#c9d1d9', fontsize=14, pad=15, fontweight='bold')
    ax.set_xlabel("Fiber Distance (km)", color='#8b949e', fontsize=12, fontweight='bold')
    ax.set_ylabel("Secure Key Rate (bits/sec)", color='#8b949e', fontsize=12, fontweight='bold')
    ax.grid(True, linestyle='--', color='#30363d', alpha=0.5)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#30363d')
    ax.spines['left'].set_color('#30363d')
    
    ax.legend(facecolor='#0d1117', edgecolor='#30363d', labelcolor='white')
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    
    return send_file(buf, mimetype='image/png')