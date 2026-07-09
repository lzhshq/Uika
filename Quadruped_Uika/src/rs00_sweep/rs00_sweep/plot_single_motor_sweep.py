#!/usr/bin/env python3
"""Generate a PDF report for single-motor sweep CSV files."""

import argparse
import csv
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def _float(row, key, default=0.0):
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def load_csv(csv_file):
    with open(csv_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames or []

    joint_names = [
        name[:-len('_cmd_pos')]
        for name in headers
        if name.endswith('_cmd_pos')
    ]
    if not rows or not joint_names:
        raise RuntimeError('CSV has no sweep records or motor columns')

    target_name = rows[0].get('target_name', '')
    if not target_name or target_name not in joint_names:
        try:
            target_index = int(float(rows[0].get('target_index', 0)))
            target_name = joint_names[target_index]
        except (ValueError, IndexError):
            target_name = joint_names[0]

    data = {
        'time': [_float(row, 'time') for row in rows],
        'frequency': [_float(row, 'current_frequency') for row in rows],
        'signal': [_float(row, 'sweep_signal') for row in rows],
        'phase': [row.get('phase', '') for row in rows],
        'target_name': target_name,
        'target_index': rows[0].get('target_index', ''),
        'target_kp': rows[0].get('target_kp', ''),
        'target_kd': rows[0].get('target_kd', ''),
        'hold_kp': rows[0].get('hold_kp', ''),
        'hold_kd': rows[0].get('hold_kd', ''),
        'joints': {},
    }
    for joint in joint_names:
        data['joints'][joint] = {
            'cmd_pos': [_float(row, f'{joint}_cmd_pos') for row in rows],
            'fb_pos': [_float(row, f'{joint}_fb_pos') for row in rows],
            'fb_vel': [_float(row, f'{joint}_fb_vel') for row in rows],
            'fb_torque': [_float(row, f'{joint}_fb_torque') for row in rows],
            'fb_temp': [_float(row, f'{joint}_fb_temp') for row in rows],
        }
    return data


def plot_report(csv_file, output_pdf=None):
    data = load_csv(csv_file)
    if output_pdf is None:
        output_pdf = os.path.splitext(csv_file)[0] + '.pdf'

    try:
        plt.style.use('seaborn-v0_8-darkgrid')
    except Exception:
        plt.style.use('default')

    time = data['time']
    target = data['target_name']
    target_data = data['joints'][target]

    with PdfPages(output_pdf) as pdf:
        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        fig.suptitle(
            f'Single Motor Sweep: {target} | '
            f'target kp/kd={data["target_kp"]}/{data["target_kd"]}, '
            f'hold kp/kd={data["hold_kp"]}/{data["hold_kd"]}',
            fontsize=13,
            fontweight='bold',
        )
        axes[0].plot(time, target_data['cmd_pos'], label='cmd position', linewidth=1.2)
        axes[0].plot(time, target_data['fb_pos'], label='feedback position', linewidth=1.2)
        axes[0].set_ylabel('Position (rad)')
        axes[0].legend(loc='best')

        axes[1].plot(time, data['frequency'], label='frequency', color='tab:purple')
        axes[1].set_ylabel('Frequency (Hz)')
        axes[1].legend(loc='best')

        ax_vel = axes[2]
        ax_torque = ax_vel.twinx()
        vel_line = ax_vel.plot(time, target_data['fb_vel'], label='feedback velocity', color='tab:green')
        torque_line = ax_torque.plot(time, target_data['fb_torque'], label='feedback torque', color='tab:orange')
        ax_vel.set_ylabel('Velocity (rad/s)', color='tab:green')
        ax_torque.set_ylabel('Torque (Nm)', color='tab:orange')
        ax_vel.set_xlabel('Time (s)')
        lines = vel_line + torque_line
        ax_vel.legend(lines, [line.get_label() for line in lines], loc='best')
        fig.tight_layout()
        pdf.savefig(fig, bbox_inches='tight', dpi=150)
        plt.close(fig)

        joints = list(data['joints'].keys())
        fig, axes = plt.subplots(len(joints), 1, figsize=(12, max(10, len(joints) * 1.8)), sharex=True)
        if len(joints) == 1:
            axes = [axes]
        for ax, joint in zip(axes, joints):
            joint_data = data['joints'][joint]
            ax.plot(time, joint_data['cmd_pos'], label='cmd', linewidth=0.9)
            ax.plot(time, joint_data['fb_pos'], label='feedback', linewidth=0.9)
            ax.set_ylabel(joint, fontsize=8)
            ax.grid(True, alpha=0.3)
            if joint == target:
                ax.set_title(f'{joint} (swept target)', fontsize=9, fontweight='bold')
            else:
                ax.set_title(f'{joint} (hold)', fontsize=9)
        axes[-1].set_xlabel('Time (s)')
        axes[0].legend(loc='best', fontsize=8)
        fig.suptitle('All Joint Position Commands vs Feedback', fontsize=13, fontweight='bold')
        fig.tight_layout()
        pdf.savefig(fig, bbox_inches='tight', dpi=150)
        plt.close(fig)

    print(f'PDF report saved to: {output_pdf}')
    return output_pdf


def main():
    parser = argparse.ArgumentParser(description='Plot single motor sweep CSV data')
    parser.add_argument('csv_file', help='Input CSV file')
    parser.add_argument('-o', '--output', default=None, help='Output PDF file')
    args = parser.parse_args()

    if not os.path.exists(args.csv_file):
        print(f'CSV file not found: {args.csv_file}', file=sys.stderr)
        sys.exit(1)
    try:
        plot_report(args.csv_file, args.output)
    except Exception as exc:  # noqa: BLE001
        print(f'Plotting failed: {exc}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
