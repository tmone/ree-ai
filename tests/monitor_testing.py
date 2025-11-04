#!/usr/bin/env python3
"""
Real-time Testing Monitor Dashboard
Watches test logs and displays live statistics
"""
import os
import time
import sys
from datetime import datetime
from collections import defaultdict

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def read_stats():
    """Read statistics from CSV file"""
    stats_file = "test_logs/stats.csv"
    if not os.path.exists(stats_file):
        return []

    with open(stats_file, 'r') as f:
        lines = f.readlines()

    stats = []
    for line in lines:
        parts = line.strip().split(',')
        if len(parts) == 4:
            stats.append({
                'iteration': int(parts[0]),
                'bugs': int(parts[1]),
                'slow_queries': int(parts[2]),
                'timestamp': int(parts[3])
            })
    return stats

def read_bug_alerts():
    """Read recent bug alerts"""
    alerts_file = "test_logs/bug_alerts.log"
    if not os.path.exists(alerts_file):
        return []

    with open(alerts_file, 'r') as f:
        lines = f.readlines()

    return lines[-10:]  # Last 10 alerts

def display_dashboard(stats, alerts):
    """Display real-time dashboard"""
    clear_screen()

    print("╔" + "="*78 + "╗")
    print("║" + "CONTINUOUS TESTING MONITOR - REE AI ORCHESTRATOR".center(78) + "║")
    print("║" + f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(78) + "║")
    print("╚" + "="*78 + "╝")
    print()

    if not stats:
        print("⏳ Waiting for test data...")
        print("   (Test loop needs to complete at least one iteration)")
        return

    # Overall statistics
    total_iterations = len(stats)
    total_bugs = sum(s['bugs'] for s in stats)
    total_slow = sum(s['slow_queries'] for s in stats)

    if stats:
        start_time = datetime.fromtimestamp(stats[0]['timestamp'])
        last_time = datetime.fromtimestamp(stats[-1]['timestamp'])
        duration = (last_time - start_time).total_seconds()
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
    else:
        hours = minutes = 0

    print("📊 OVERALL STATISTICS")
    print("─" * 80)
    print(f"  Total Iterations:   {total_iterations}")
    print(f"  Total Bugs Found:   {total_bugs}")
    print(f"  Total Slow Queries: {total_slow}")
    print(f"  Runtime:            {hours}h {minutes}m")
    print()

    # Recent iterations (last 10)
    print("📈 RECENT ITERATIONS (Last 10)")
    print("─" * 80)
    print(f"{'Iter':<8} {'Bugs':<8} {'Slow':<8} {'Time':<20} {'Status':<20}")
    print("─" * 80)

    recent_stats = stats[-10:]
    for s in recent_stats:
        iter_num = s['iteration']
        bugs = s['bugs']
        slow = s['slow_queries']
        timestamp = datetime.fromtimestamp(s['timestamp']).strftime('%H:%M:%S')

        if bugs > 5:
            status = "🔴 High Bug Count"
        elif bugs > 0:
            status = "🟡 Bugs Detected"
        else:
            status = "✅ Clean"

        print(f"{iter_num:<8} {bugs:<8} {slow:<8} {timestamp:<20} {status:<20}")

    print()

    # Trends
    if len(stats) >= 5:
        last_5_bugs = sum(s['bugs'] for s in stats[-5:]) / 5
        last_5_slow = sum(s['slow_queries'] for s in stats[-5:]) / 5

        print("📉 TRENDS (Last 5 iterations)")
        print("─" * 80)
        print(f"  Average Bugs:        {last_5_bugs:.1f} per iteration")
        print(f"  Average Slow Queries: {last_5_slow:.1f} per iteration")

        if last_5_bugs > 3:
            print(f"  ⚠️  Bug rate is HIGH - system needs attention")
        elif last_5_bugs > 1:
            print(f"  🟡 Bug rate is MODERATE - monitoring recommended")
        else:
            print(f"  ✅ Bug rate is LOW - system stable")
        print()

    # Recent alerts
    if alerts:
        print("🚨 RECENT ALERTS (Last 10)")
        print("─" * 80)
        for alert in alerts[-10:]:
            print(f"  {alert.strip()}")
        print()

    # Instructions
    print("─" * 80)
    print("Press Ctrl+C to stop monitoring | Refreshes every 10 seconds")
    print("─" * 80)

def main():
    """Main monitoring loop"""
    print("Starting monitoring dashboard...")
    print("Waiting for test data...\n")

    try:
        while True:
            stats = read_stats()
            alerts = read_bug_alerts()
            display_dashboard(stats, alerts)
            time.sleep(10)  # Refresh every 10 seconds

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
