import json
import os
import sys
from collections import Counter

# Add backend to path
sys.path.append(os.getcwd())

from app.analysis.threat_engine import analyze_threat

def run_mass_test(input_file='test_suite_1000.json'):
    if not os.path.exists(input_file):
        print(f"[!] Error: {input_file} not found. Run generate_cases.py first.")
        return

    with open(input_file, 'r') as f:
        cases = json.load(f)

    results = []
    stats = {
        'total': 0,
        'detected': 0,
        'missed': 0,
        'by_category': {},
        'severity_dist': Counter()
    }

    print(f"[*] Starting mass evaluation of {len(cases)} cases...")

    for case in cases:
        analysis = analyze_threat(case['description'])
        
        # Determine success
        is_detected = analysis['score'] > 0
        stats['total'] += 1
        
        if is_detected:
            stats['detected'] += 1
        else:
            stats['missed'] += 1
            
        stats['severity_dist'][analysis['severity']] += 1
        
        # Categorical accuracy
        expected = case['expected_category']
        if expected not in stats['by_category']:
            stats['by_category'][expected] = {'total': 0, 'detected': 0}
            
        stats['by_category'][expected]['total'] += 1
        if is_detected:
             # Basic check: did we detect the correct vector?
             if expected.lower() in [v.lower() for v in analysis['attack_vectors']]:
                 stats['by_category'][expected]['detected'] += 1

        results.append({
            'id': case['id'],
            'expected': expected,
            'description': case['description'],
            'analysis': {
                'score': analysis['score'],
                'severity': analysis['severity'],
                'vectors': analysis['attack_vectors'],
                'type': analysis['attack_type']
            }
        })

    # Summary calculation
    summary = {
        'overall': {
            'total_cases': stats['total'],
            'detection_rate': f"{(stats['detected']/stats['total'])*100:.2f}%",
            'miss_rate': f"{(stats['missed']/stats['total'])*100:.2f}%"
        },
        'severity_distribution': dict(stats['severity_dist']),
        'category_performance': {}
    }

    for cat, data in stats['by_category'].items():
        rate = (data['detected'] / data['total']) * 100 if data['total'] > 0 else 0
        summary['category_performance'][cat] = {
            'total': data['total'],
            'detected': data['detected'],
            'recall': f"{rate:.2f}%"
        }

    with open('test_results_summary.json', 'w') as f:
        json.dump(summary, f, indent=4)
        
    with open('test_results_detailed.json', 'w') as f:
        json.dump(results, f, indent=4)

    print("\n[+] MASS TEST COMPLETE")
    print(f"Detection Rate: {summary['overall']['detection_rate']}")
    print("-" * 30)
    for cat, s in summary['category_performance'].items():
        print(f"{cat:20} : {s['recall']} recall")
    print("-" * 30)
    print(f"Detailed logs saved to test_results_detailed.json")

if __name__ == "__main__":
    run_mass_test()
