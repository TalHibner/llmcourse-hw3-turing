"""Main entry point for the translation pipeline."""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

from src.utils.config import load_config
from src.input.generator import TestCaseGenerator
from src.agents.pipeline import TranslationPipeline
from src.analysis.embeddings import SemanticAnalyzer
from src.visualization.plots import Visualizer


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Translation System with Error Analysis"
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--mode',
        type=str,
        default='full',
        choices=['full', 'analyze', 'visualize'],
        help='Execution mode'
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Input file for analyze/visualize modes'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of test cases (for testing)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    print("\n" + "="*60)
    print("Multi-Agent Translation System with Error Analysis")
    print("="*60 + "\n")

    # Load configuration
    print(f"Loading configuration from: {args.config}")
    config = load_config(args.config)

    if args.mode == 'full':
        run_full_pipeline(config, args)
    elif args.mode == 'analyze':
        run_analysis_only(config, args)
    elif args.mode == 'visualize':
        run_visualization_only(config, args)


def run_full_pipeline(config: dict, args):
    """Run the complete pipeline."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Step 1: Generate test cases
    print("\n" + "="*60)
    print("STEP 1: Generating Test Cases")
    print("="*60)

    base_sentences_file = config['input']['base_sentences_file']
    error_rates = config['input']['error_rates']

    generator = TestCaseGenerator(base_sentences_file)
    test_cases = generator.generate_test_cases(error_rates)

    if args.limit:
        test_cases = test_cases[:args.limit]
        print(f"\nLimited to {args.limit} test cases")

    print(f"\nGenerated {len(test_cases)} test cases")
    print(f"Error rates: {error_rates}")

    # Save test cases
    test_cases_file = f"data/test_cases_{timestamp}.json"
    generator.save_test_cases(test_cases, test_cases_file)
    print(f"Test cases saved to: {test_cases_file}")

    # Step 2: Run translation pipeline
    print("\n" + "="*60)
    print("STEP 2: Running Translation Pipeline")
    print("="*60)

    pipeline = TranslationPipeline(config)
    results = pipeline.process_batch(test_cases)

    # Save translation results
    results_file = f"results/translations/translations_{timestamp}.json"
    Path(results_file).parent.mkdir(parents=True, exist_ok=True)
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nTranslation results saved to: {results_file}")

    # Step 3: Analyze semantic distances
    print("\n" + "="*60)
    print("STEP 3: Analyzing Semantic Distances")
    print("="*60)

    analyzer = SemanticAnalyzer(config['analysis']['embedding_model'])
    metric = config['analysis']['distance_metric']

    analysis_data = []
    for result in results:
        if result.get('metadata', {}).get('success'):
            original = result['test_case']['original_clean']
            final = result['final']
            error_rate = result['test_case']['actual_error_rate']

            distance = analyzer.calculate_distance(original, final, metric)

            analysis_data.append({
                'test_id': result['test_id'],
                'error_rate': error_rate,
                'target_error_rate': result['test_case']['target_error_rate'],
                'distance': distance,
                'original': original,
                'final': final,
                'word_count': result['test_case']['word_count']
            })

            print(f"Test {result['test_id']}: Error Rate={error_rate:.2%}, Distance={distance:.4f}")

    # Convert to DataFrame
    df = pd.DataFrame(analysis_data)

    # Save analysis results
    analysis_file = f"results/analysis/analysis_{timestamp}.csv"
    Path(analysis_file).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(analysis_file, index=False)
    print(f"\nAnalysis results saved to: {analysis_file}")

    # Step 4: Generate visualizations
    print("\n" + "="*60)
    print("STEP 4: Generating Visualizations")
    print("="*60)

    visualizer = Visualizer(
        output_dir=config['output']['results_dir'] + "/graphs",
        dpi=config['visualization']['dpi']
    )

    graph_file = f"error_distance_graph_{timestamp}.png"
    graph_path = visualizer.plot_error_distance_relationship(df, graph_file)

    # Generate summary statistics
    stats = visualizer.create_summary_statistics(df)

    # Save summary
    summary_file = f"results/analysis/summary_{timestamp}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("ANALYSIS SUMMARY\n")
        f.write("="*60 + "\n\n")

        f.write(f"Total Test Cases: {stats['overall']['total_cases']}\n")
        f.write(f"Mean Distance: {stats['overall']['mean_distance']:.4f}\n")
        f.write(f"Std Distance: {stats['overall']['std_distance']:.4f}\n")
        f.write(f"Min Distance: {stats['overall']['min_distance']:.4f}\n")
        f.write(f"Max Distance: {stats['overall']['max_distance']:.4f}\n")
        f.write(f"Correlation (error_rate vs distance): {stats['overall']['correlation']:.4f}\n")

        f.write("\n" + "="*60 + "\n")
        f.write("BY ERROR RATE\n")
        f.write("="*60 + "\n\n")

        for error_rate, stats_dict in sorted(stats['by_error_rate']['mean'].items()):
            f.write(f"\nError Rate: {error_rate:.1%}\n")
            f.write(f"  Count: {stats['by_error_rate']['count'][error_rate]}\n")
            f.write(f"  Mean: {stats_dict:.4f}\n")
            f.write(f"  Std: {stats['by_error_rate']['std'][error_rate]:.4f}\n")
            f.write(f"  Min: {stats['by_error_rate']['min'][error_rate]:.4f}\n")
            f.write(f"  Max: {stats['by_error_rate']['max'][error_rate]:.4f}\n")

    print(f"Summary saved to: {summary_file}")

    # Final summary
    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)
    print(f"\nResults saved to:")
    print(f"  - Translations: {results_file}")
    print(f"  - Analysis: {analysis_file}")
    print(f"  - Graph: {graph_path}")
    print(f"  - Summary: {summary_file}")
    print(f"\nCorrelation: {stats['overall']['correlation']:.4f}")
    print("\nCheck the graph to see the relationship between error rate and semantic drift!")


def run_analysis_only(config: dict, args):
    """Run analysis on existing translation results."""
    if not args.input:
        print("Error: --input required for analyze mode")
        sys.exit(1)

    print(f"Loading translations from: {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        results = json.load(f)

    # Analyze
    analyzer = SemanticAnalyzer(config['analysis']['embedding_model'])
    metric = config['analysis']['distance_metric']

    analysis_data = []
    for result in results:
        if result.get('metadata', {}).get('success'):
            original = result['test_case']['original_clean']
            final = result['final']
            error_rate = result['test_case']['actual_error_rate']

            distance = analyzer.calculate_distance(original, final, metric)

            analysis_data.append({
                'test_id': result['test_id'],
                'error_rate': error_rate,
                'distance': distance,
                'original': original,
                'final': final
            })

    df = pd.DataFrame(analysis_data)

    # Save
    output_file = args.input.replace('.json', '_analysis.csv')
    df.to_csv(output_file, index=False)
    print(f"Analysis saved to: {output_file}")


def run_visualization_only(config: dict, args):
    """Generate visualizations from existing analysis."""
    if not args.input:
        print("Error: --input required for visualize mode")
        sys.exit(1)

    print(f"Loading analysis from: {args.input}")
    df = pd.DataFrame(pd.read_csv(args.input))

    visualizer = Visualizer(
        output_dir=config['output']['results_dir'] + "/graphs",
        dpi=config['visualization']['dpi']
    )

    graph_path = visualizer.plot_error_distance_relationship(df)
    print(f"Graph saved to: {graph_path}")


if __name__ == "__main__":
    main()
