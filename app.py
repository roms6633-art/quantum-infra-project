import matplotlib
matplotlib.use('Agg')

from flask import Flask, jsonify, request, send_file
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error # הספריות החדשות לרעש הפיזיקלי
import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec

app = Flask(__name__)

def perform_qkd_logic(num_bits, eavesdropper):
    alice_bits = np.random.randint(2, size=num_bits)
    alice_bases = np.random.randint(2, size=num_bits) 
    bob_bases = np.random.randint(2, size=num_bits)

    qc = QuantumCircuit(num_bits, num_bits)

    for i in range(num_bits):
        if alice_bits[i] == 1: qc.x(i)
        if alice_bases[i] == 1: qc.h(i)

    if eavesdropper:
        eve_bases = np.random.randint(2, size=num_bits)
        for i in range(num_bits):
            if eve_bases[i] == 1: qc.h(i)
            qc.measure(i, i) 
            if eve_bases[i] == 1: qc.h(i)

    for i in range(num_bits):
        if bob_bases[i] == 1: qc.h(i)
        qc.measure(i, i)

    # --- הזרקת מודל הרעש הפיזיקלי לחומרה ---
    noise_model = NoiseModel()
    # אנחנו מגדירים הסתברות שגיאה של 3% על השערים כדי לדמות חוסר דיוק בחומרה האמיתית
    error_gate = depolarizing_error(0.03, 1) 
    noise_model.add_all_qubit_quantum_error(error_gate, ['x', 'h'])

    # טוענים את הסימולטור יחד עם מודל הרעש שבנינו
    simulator = AerSimulator(noise_model=noise_model)
    # ----------------------------------------

    compiled_circuit = transpile(qc, simulator)
    result = simulator.run(compiled_circuit, shots=1).result()
    
    measured_bits_str = list(result.get_counts().keys())[0][::-1] 
    bob_bits = [int(b) for b in measured_bits_str]

    sifted_key_alice = []
    sifted_key_bob = []
    matching_indices = []
    for i in range(num_bits):
        if alice_bases[i] == bob_bases[i]:
            sifted_key_alice.append(int(alice_bits[i]))
            sifted_key_bob.append(int(bob_bits[i]))
            matching_indices.append(i)

    errors = sum(1 for a, b in zip(sifted_key_alice, sifted_key_bob) if a != b)
    error_indices = [idx for idx, (a, b) in zip(matching_indices, zip(sifted_key_alice, sifted_key_bob)) if a != b]
    qber = (errors / len(sifted_key_alice)) if len(sifted_key_alice) > 0 else 0
    secure = bool(qber < 0.1)

    return {
        "num_bits": num_bits, "eavesdropper": eavesdropper,
        "alice_bits": alice_bits, "alice_bases": alice_bases,
        "bob_bases": bob_bases, "bob_bits": bob_bits,
        "matching_indices": matching_indices,
        "alice_key": sifted_key_alice, "bob_key": sifted_key_bob,
        "error_indices": error_indices, "qber": qber, "secure": secure
    }

def get_bloch_vector(bit, base):
    if base == 0 and bit == 0: return [0, 0, 1]   
    if base == 0 and bit == 1: return [0, 0, -1]  
    if base == 1 and bit == 0: return [1, 0, 0]   
    if base == 1 and bit == 1: return [-1, 0, 0]  
    return [0, 0, 0]

@app.route('/qkd/visualize', methods=['GET'])
def visualize_qkd():
    num_bits = int(request.args.get('bits', 16))
    eavesdropper = request.args.get('eve', 'false').lower() == 'true'
    
    if num_bits > 28: return jsonify({"error": "Too many bits for visualization"}), 400
    
    data = perform_qkd_logic(num_bits, eavesdropper)
    
    plt.style.use('dark_background')
    fig_width = max(num_bits * 0.5, 12) 
    fig = plt.figure(figsize=(fig_width, 14))
    
    fig.patch.set_facecolor('#0d1117')
    
    gs = gridspec.GridSpec(7, 1, height_ratios=[1, 1, 1, 1, 0.5, 1, 4])
    
    axs = [fig.add_subplot(gs[i]) for i in range(6)]
    ax_bloch = fig.add_subplot(gs[6], projection='3d')
    plt.subplots_adjust(hspace=0.6)

    for ax in axs:
        ax.set_facecolor('#0d1117') 
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#30363d')
        ax.spines['left'].set_color('#30363d')

    status_color = '#39d353' if data['secure'] else '#f85149'
    status_text = "SECURE (No Eve detected)" if data['secure'] else "BREACHED (Eve detected!)"
    
    # הוספתי אינדיקציה בכותרת שמודל הרעש מופעל
    fig.suptitle(f"Quantum Security Dashboard (BB84)\nStatus: {status_text} | Error Rate: {data['qber']:.1%} | Hardware Noise: Active", 
                 fontsize=18, fontweight='bold', color=status_color, y=0.95)

    subtitle_color = '#c9d1d9'
    bit_colors = {0: '#1f6feb', 1: '#238636'}
    base_symbols = {0: '+', 1: 'x'}

    def draw_row(ax, y_values, markers, colors, title, show_grid=True):
        ax.set_title(title, loc='left', fontsize=12, fontweight='bold', color=subtitle_color)
        ax.set_ylim(-0.5, 0.5); ax.set_yticks([])
        ax.set_xlim(-0.5, num_bits - 0.5); ax.set_xticks(range(num_bits))
        if show_grid: ax.grid(True, axis='x', linestyle='--', color='#30363d', alpha=0.5)
        for i in range(num_bits):
            rect = patches.Rectangle((i-0.4, -0.4), 0.8, 0.8, color=colors[i], alpha=0.8)
            ax.add_patch(rect)
            ax.text(i, 0, markers[i], ha='center', va='center', fontsize=14, fontweight='bold', color='white')

    draw_row(axs[0], data['alice_bits'], [base_symbols[b] for b in data['alice_bases']], [bit_colors[b] for b in data['alice_bits']], "1. Alice Sent")
    
    axs[1].set_title("2. Quantum Channel", loc='left', fontsize=12, color=subtitle_color)
    
    if eavesdropper:
        axs[1].text(num_bits/2, -0.3, "⚠️ EVE INTERCEPTED AND MEASURED! ⚠️", ha='center', va='center', color='#f85149', fontsize=14, fontweight='bold')
        for i in range(num_bits): axs[1].scatter(i, 0, marker='X', color='#f85149', s=50, alpha=0.6)
    else:
        axs[1].text(num_bits/2, 0, "---> Clean Quantum Channel --->", ha='center', va='center', color='#58a6ff', fontsize=12)
    
    axs[1].set_ylim(-0.8, 0.5) 
    axs[1].set_yticks([]); axs[1].set_xlim(-0.5, num_bits - 0.5); axs[1].set_xticks(range(num_bits))
    axs[1].grid(True, axis='x', linestyle='--', color='#30363d', alpha=0.5)

    draw_row(axs[2], data['bob_bits'], [base_symbols[b] for b in data['bob_bases']], [bit_colors[b] for b in data['bob_bits']], "3. Bob Received")
    
    axs[3].set_title("4. Basis Sifting (Highlighting matches)", loc='left', fontsize=12, color=subtitle_color)
    axs[3].set_ylim(-0.5, 0.5); axs[3].set_yticks([]); axs[3].set_xlim(-0.5, num_bits - 0.5)
    for i in range(num_bits):
        if i in data['matching_indices']:
            axs[3].add_patch(patches.Rectangle((i-0.4, -0.4), 0.8, 0.8, color='#d29922', alpha=0.8)) 
            axs[3].text(i, 0, "✅", ha='center', va='center')
        else:
            axs[3].text(i, 0, "-", ha='center', va='center', color='#8b949e')

    axs[4].axis('off')
    
    axs[5].set_title("5. Final Sifted Keys Comparison (with Hardware Noise)", loc='left', fontsize=12, color=subtitle_color)
    axs[5].set_ylim(-1, 2); axs[5].set_yticks([0, 1]); axs[5].set_yticklabels(["Bob Key", "Alice Key"], fontweight='bold', color=subtitle_color)
    axs[5].set_xlim(-0.5, num_bits - 0.5); axs[5].grid(True, axis='x', linestyle='--', color='#30363d', alpha=0.5)

    for i in range(num_bits):
        if i in data['matching_indices']:
            a_bit = data['alice_bits'][i]
            b_bit = data['bob_bits'][i]
            is_error = a_bit != b_bit
            axs[5].text(i, 1, str(a_bit), ha='center', va='center', fontsize=12, color='white', bbox=dict(facecolor=bit_colors[a_bit], edgecolor='none', alpha=0.8))
            bob_bbox = dict(facecolor=bit_colors[b_bit], edgecolor='none', alpha=0.8) if not is_error else dict(facecolor='#f85149', edgecolor='white')
            axs[5].text(i, 0, str(b_bit), ha='center', va='center', fontsize=12, color='white', bbox=bob_bbox)
            if is_error: axs[5].scatter(i, 0.5, marker='X', color='#f85149', s=100)

    ax_bloch.set_title("Vulnerability Analysis: Quantum State on Bloch Sphere", fontsize=14, fontweight='bold', pad=0, y=1.15, color=subtitle_color)
    ax_bloch.set_facecolor('#0d1117') 

    u, v = np.mgrid[0:2*np.pi:30j, 0:np.pi:20j]
    x = np.cos(u)*np.sin(v); y = np.sin(u)*np.sin(v); z = np.cos(v)
    ax_bloch.plot_wireframe(x, y, z, color='#8b949e', alpha=0.15)
    ax_bloch.plot([-1.2, 1.2], [0, 0], [0, 0], color='#8b949e', linestyle='--', alpha=0.3) 
    ax_bloch.plot([0, 0], [-1.2, 1.2], [0, 0], color='#8b949e', linestyle='--', alpha=0.3) 
    ax_bloch.plot([0, 0], [0, 0], [-1.2, 1.2], color='#8b949e', linestyle='--', alpha=0.3) 
    
    ax_bloch.text(0, 0, 1.3, "|0> (Z)", ha='center', fontsize=12, color='white')
    ax_bloch.text(0, 0, -1.5, "|1> (-Z)", ha='center', fontsize=12, color='white')
    ax_bloch.text(1.5, 0, 0, "|+> (X)", ha='center', fontsize=12, color='white')
    ax_bloch.text(-1.5, 0, 0, "|-> (-X)", ha='center', fontsize=12, color='white')

    if len(data['error_indices']) > 0:
        err_idx = data['error_indices'][0]
        alice_vec = get_bloch_vector(data['alice_bits'][err_idx], data['alice_bases'][err_idx])
        bob_vec = get_bloch_vector(data['bob_bits'][err_idx], data['bob_bases'][err_idx])
        ax_bloch.quiver(0, 0, 0, alice_vec[0], alice_vec[1], alice_vec[2], color='#39d353', linewidth=4, arrow_length_ratio=0.15, label="Alice's Original State")
        ax_bloch.quiver(0, 0, 0, bob_vec[0], bob_vec[1], bob_vec[2], color='#f85149', linewidth=4, arrow_length_ratio=0.15, label="Collapsed/Noisy State (Measured by Bob)")
        ax_bloch.text2D(0.05, 0.85, f"Showing error at Bit Index {err_idx}:\nQuantum state was altered due to Eve's measurement\nor natural hardware decoherence!", transform=ax_bloch.transAxes, color='#f85149', fontsize=11, fontweight='bold', bbox=dict(facecolor='#0d1117', alpha=0.8, edgecolor='none'))
    elif len(data['matching_indices']) > 0:
        good_idx = data['matching_indices'][0]
        vec = get_bloch_vector(data['alice_bits'][good_idx], data['alice_bases'][good_idx])
        ax_bloch.quiver(0, 0, 0, vec[0], vec[1], vec[2], color='#58a6ff', linewidth=4, arrow_length_ratio=0.15, label="Preserved Quantum State")
        ax_bloch.text2D(0.05, 0.85, "Perfect Transmission!\nThe quantum state remained intact.", transform=ax_bloch.transAxes, color='#39d353', fontsize=11, fontweight='bold', bbox=dict(facecolor='#0d1117', alpha=0.8, edgecolor='none'))

    ax_bloch.set_axis_off()
    
    legend = ax_bloch.legend(loc='lower center', facecolor='#0d1117', edgecolor='#30363d')
    for text in legend.get_texts():
        text.set_color('white')

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)

    return send_file(buf, mimetype='image/png')

@app.route('/health')
def health_check():
    return jsonify({"status": "Healthy", "service": "Quantum Security Visualization API"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)