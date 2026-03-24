import matplotlib
matplotlib.use('Agg')

from flask import Blueprint, jsonify, request, send_file
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec

# הגדרת ה-Blueprint
monitor_bp = Blueprint('monitor', __name__)

def perform_qkd_logic(num_bits, eavesdropper, protocol='bb84'):
    # ... (כל הלוגיקה המקורית של QKD ותיקון שגיאות שהייתה לנו קודם) ...
    alice_bases = np.random.randint(2, size=num_bits) 
    bob_bases = np.random.randint(2, size=num_bits)
    alice_bits = []; bob_bits = []

    noise_model = NoiseModel()
    error_gate = depolarizing_error(0.03, 1) 
    noise_model.add_all_qubit_quantum_error(error_gate, ['x', 'h'])
    simulator = AerSimulator(noise_model=noise_model)

    if protocol == 'bb84':
        alice_bits_prep = np.random.randint(2, size=num_bits)
        for i in range(num_bits):
            qc = QuantumCircuit(1, 1)
            if alice_bits_prep[i] == 1: qc.x(0)
            if alice_bases[i] == 1: qc.h(0)

            if eavesdropper:
                eve_base = np.random.randint(2)
                if eve_base == 1: qc.h(0)
                qc.measure(0, 0) 
                if eve_base == 1: qc.h(0)

            if bob_bases[i] == 1: qc.h(0)
            qc.measure(0, 0)
            
            compiled_circuit = transpile(qc, simulator)
            result = simulator.run(compiled_circuit, shots=1).result()
            bob_bits.append(int(list(result.get_counts().keys())[0]))
        alice_bits = list(alice_bits_prep)
            
    elif protocol == 'e91':
        for i in range(num_bits):
            qc = QuantumCircuit(2, 2)
            qc.h(0)
            qc.cx(0, 1) 
            
            if eavesdropper:
                eve_base = np.random.randint(2)
                if eve_base == 1: qc.h(1)
                qc.measure(1, 1)
                if eve_base == 1: qc.h(1)

            if alice_bases[i] == 1: qc.h(0)
            qc.measure(0, 0)
            
            if bob_bases[i] == 1: qc.h(1)
            qc.measure(1, 1)

            compiled_circuit = transpile(qc, simulator)
            result = simulator.run(compiled_circuit, shots=1).result()
            measured_bits_str = list(result.get_counts().keys())[0].zfill(2)[::-1]
            alice_bits.append(int(measured_bits_str[0]))
            bob_bits.append(int(measured_bits_str[1]))

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

    reconciled_bob_key = list(sifted_key_bob)
    fixed_indices = []
    if secure and qber > 0:
        for i in range(len(reconciled_bob_key)):
            if sifted_key_alice[i] != reconciled_bob_key[i]:
                reconciled_bob_key[i] = sifted_key_alice[i] 
                fixed_indices.append(matching_indices[i]) 

    return {
        "num_bits": num_bits, "eavesdropper": eavesdropper, "protocol": protocol.upper(),
        "alice_bits": alice_bits, "alice_bases": alice_bases,
        "bob_bases": bob_bases, "bob_bits": bob_bits,
        "matching_indices": matching_indices,
        "alice_key": sifted_key_alice, "bob_key": sifted_key_bob,
        "reconciled_bob_key": reconciled_bob_key, "fixed_indices": fixed_indices,
        "error_indices": error_indices, "qber": qber, "secure": secure
    }

def get_bloch_vector(bit, base):
    if base == 0 and bit == 0: return [0, 0, 1]   
    if base == 0 and bit == 1: return [0, 0, -1]  
    if base == 1 and bit == 0: return [1, 0, 0]   
    if base == 1 and bit == 1: return [-1, 0, 0]  
    return [0, 0, 0]

# משתמשים ב-monitor_bp במקום ב-app!
@monitor_bp.route('/qkd/visualize', methods=['GET'])
def visualize_qkd():
    num_bits = int(request.args.get('bits', 16))
    eavesdropper = request.args.get('eve', 'false').lower() == 'true'
    protocol = request.args.get('protocol', 'bb84').lower()
    
    data = perform_qkd_logic(num_bits, eavesdropper, protocol)
    
    plt.style.use('dark_background')
    fig_width = max(num_bits * 0.5, 12) 
    fig = plt.figure(figsize=(fig_width, 16)) 
    fig.patch.set_facecolor('#0d1117')
    
    gs = gridspec.GridSpec(8, 1, height_ratios=[1, 1, 1, 1, 0.5, 1, 1, 4])
    axs = [fig.add_subplot(gs[i]) for i in range(7)]
    ax_bloch = fig.add_subplot(gs[7], projection='3d')
    plt.subplots_adjust(hspace=0.6)

    for ax in axs:
        ax.set_facecolor('#0d1117') 
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#30363d')
        ax.spines['left'].set_color('#30363d')

    status_color = '#39d353' if data['secure'] else '#f85149'
    status_text = "SECURE (No Eve detected)" if data['secure'] else "BREACHED (Eve detected!)"
    
    fig.suptitle(f"Quantum Security Dashboard ({data['protocol']})\nStatus: {status_text} | Error Rate: {data['qber']:.1%} | Hardware Noise: Active", 
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

    alice_title = "1. Alice Measured (Entangled State)" if protocol == 'e91' else "1. Alice Sent"
    draw_row(axs[0], data['alice_bits'], [base_symbols[b] for b in data['alice_bases']], [bit_colors[b] for b in data['alice_bits']], alice_title)
    
    axs[1].set_title("2. Quantum Channel", loc='left', fontsize=12, color=subtitle_color)
    if eavesdropper:
        axs[1].text(num_bits/2, -0.3, "⚠️ EVE INTERCEPTED AND MEASURED! ⚠️", ha='center', va='center', color='#f85149', fontsize=14, fontweight='bold')
        for i in range(num_bits): axs[1].scatter(i, 0, marker='X', color='#f85149', s=50, alpha=0.6)
    else:
        channel_text = "---> Entangled Particles Transmitted --->" if protocol == 'e91' else "---> Clean Quantum Channel --->"
        axs[1].text(num_bits/2, 0, channel_text, ha='center', va='center', color='#58a6ff', fontsize=12)
    axs[1].set_ylim(-0.8, 0.5); axs[1].set_yticks([]); axs[1].set_xlim(-0.5, num_bits - 0.5)
    axs[1].grid(True, axis='x', linestyle='--', color='#30363d', alpha=0.5)

    draw_row(axs[2], data['bob_bits'], [base_symbols[b] for b in data['bob_bases']], [bit_colors[b] for b in data['bob_bits']], "3. Bob Received & Measured")
    
    axs[3].set_title("4. Basis Sifting (Highlighting matches)", loc='left', fontsize=12, color=subtitle_color)
    axs[3].set_ylim(-0.5, 0.5); axs[3].set_yticks([]); axs[3].set_xlim(-0.5, num_bits - 0.5)
    for i in range(num_bits):
        if i in data['matching_indices']:
            axs[3].add_patch(patches.Rectangle((i-0.4, -0.4), 0.8, 0.8, color='#d29922', alpha=0.8)) 
            axs[3].text(i, 0, "✅", ha='center', va='center')
        else:
            axs[3].text(i, 0, "-", ha='center', va='center', color='#8b949e')

    axs[4].axis('off')
    
    axs[5].set_title("5. Raw Keys (with Hardware Noise)", loc='left', fontsize=12, color=subtitle_color)
    axs[5].set_ylim(-1, 2); axs[5].set_yticks([0, 1]); axs[5].set_yticklabels(["Bob Raw", "Alice Key"], fontweight='bold', color=subtitle_color)
    axs[5].set_xlim(-0.5, num_bits - 0.5); axs[5].grid(True, axis='x', linestyle='--', color='#30363d', alpha=0.5)

    bob_key_idx = 0
    for i in range(num_bits):
        if i in data['matching_indices']:
            a_bit = data['alice_bits'][i]
            b_bit = data['bob_bits'][i]
            is_error = a_bit != b_bit
            axs[5].text(i, 1, str(a_bit), ha='center', va='center', fontsize=12, color='white', bbox=dict(facecolor=bit_colors[a_bit], edgecolor='none', alpha=0.8))
            bob_bbox = dict(facecolor=bit_colors[b_bit], edgecolor='none', alpha=0.8) if not is_error else dict(facecolor='#f85149', edgecolor='white')
            axs[5].text(i, 0, str(b_bit), ha='center', va='center', fontsize=12, color='white', bbox=bob_bbox)
            if is_error: axs[5].scatter(i, 0.5, marker='X', color='#f85149', s=100)
            bob_key_idx += 1

    axs[6].set_title("6. Error Reconciliation (Parity Correction over Public Channel)", loc='left', fontsize=12, color='#e3b341')
    axs[6].set_ylim(-0.5, 1.5); axs[6].set_yticks([0.5]); axs[6].set_yticklabels(["Bob Fixed"], fontweight='bold', color='#e3b341')
    axs[6].set_xlim(-0.5, num_bits - 0.5); axs[6].grid(True, axis='x', linestyle='--', color='#30363d', alpha=0.5)

    bob_rec_idx = 0
    for i in range(num_bits):
        if i in data['matching_indices']:
            rec_bit = data['reconciled_bob_key'][bob_rec_idx]
            was_fixed = i in data['fixed_indices']
            
            if not data['secure']:
                axs[6].text(i, 0.5, "✖", ha='center', va='center', color='#f85149', fontsize=14)
            else:
                box_color = bit_colors[rec_bit]
                edge_color = '#39d353' if was_fixed else 'none'
                line_width = 3 if was_fixed else 0
                
                axs[6].text(i, 0.5, str(rec_bit), ha='center', va='center', fontsize=12, color='white', 
                            bbox=dict(facecolor=box_color, edgecolor=edge_color, linewidth=line_width, alpha=0.8))
                if was_fixed:
                    axs[6].text(i, 1.2, "Fixed!", ha='center', va='center', color='#39d353', fontsize=10, fontweight='bold')
            bob_rec_idx += 1

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
        ax_bloch.quiver(0, 0, 0, alice_vec[0], alice_vec[1], alice_vec[2], color='#39d353', linewidth=4, arrow_length_ratio=0.15, label="Alice's Measured State")
        ax_bloch.quiver(0, 0, 0, bob_vec[0], bob_vec[1], bob_vec[2], color='#f85149', linewidth=4, arrow_length_ratio=0.15, label="Collapsed/Noisy State")
        if data['secure']:
             ax_bloch.text2D(0.05, 0.85, f"Natural Decoherence at Bit {err_idx}.\nHardware error was successfully corrected!", transform=ax_bloch.transAxes, color='#e3b341', fontsize=11, fontweight='bold', bbox=dict(facecolor='#0d1117', alpha=0.8, edgecolor='none'))
        else:
             ax_bloch.text2D(0.05, 0.85, f"Showing error at Bit Index {err_idx}:\nQuantum state was altered due to Eve's measurement!", transform=ax_bloch.transAxes, color='#f85149', fontsize=11, fontweight='bold', bbox=dict(facecolor='#0d1117', alpha=0.8, edgecolor='none'))
    elif len(data['matching_indices']) > 0:
        good_idx = data['matching_indices'][0]
        vec = get_bloch_vector(data['alice_bits'][good_idx], data['alice_bases'][good_idx])
        label_text = "Preserved Entangled State" if protocol == 'e91' else "Preserved Quantum State"
        ax_bloch.quiver(0, 0, 0, vec[0], vec[1], vec[2], color='#58a6ff', linewidth=4, arrow_length_ratio=0.15, label=label_text)

    ax_bloch.set_axis_off()
    legend = ax_bloch.legend(loc='lower center', facecolor='#0d1117', edgecolor='#30363d')
    for text in legend.get_texts(): text.set_color('white')

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)

    return send_file(buf, mimetype='image/png')