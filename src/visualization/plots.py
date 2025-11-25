"""Visualization module for generating graphs and charts."""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional


class Visualizer:
    """Generate visualizations for analysis results."""

    def __init__(self, output_dir: str = "results/graphs", dpi: int = 300):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save graphs
            dpi: Resolution for saved images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = dpi

    def plot_error_distance_relationship(
        self,
        df: pd.DataFrame,
        output_file: str = "error_distance_graph.png",
        title: Optional[str] = None
    ) -> Path:
        """
        Generate main analysis graph: error rate vs semantic distance.

        Args:
            df: DataFrame with 'error_rate' and 'distance' columns
            output_file: Output filename
            title: Custom title (optional)

        Returns:
            Path to saved graph
        """
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))

        # Scatter plot
        scatter = ax.scatter(
            df['error_rate'] * 100,  # Convert to percentage
            df['distance'],
            s=120,
            alpha=0.6,
            c='steelblue',
            edgecolors='black',
            linewidth=0.5
        )

        # Add trend line if we have enough data points
        if len(df) > 2:
            # Group by error rate and calculate mean
            grouped = df.groupby('error_rate')['distance'].agg(['mean', 'std', 'count'])

            # Plot means with error bars
            error_rates_pct = grouped.index * 100
            means = grouped['mean']
            stds = grouped['std'].fillna(0)

            ax.errorbar(
                error_rates_pct,
                means,
                yerr=stds,
                fmt='o',
                color='darkred',
                markersize=10,
                capsize=5,
                capthick=2,
                label='Mean ± Std Dev',
                zorder=5
            )

            # Polynomial trend line
            if len(grouped) > 1:
                z = np.polyfit(error_rates_pct, means, min(2, len(grouped) - 1))
                p = np.poly1d(z)
                x_trend = np.linspace(error_rates_pct.min(), error_rates_pct.max(), 100)
                ax.plot(
                    x_trend,
                    p(x_trend),
                    'r--',
                    linewidth=2,
                    label='Trend Line',
                    alpha=0.7
                )

        # Labels and formatting
        ax.set_xlabel('Spelling Error Rate (%)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Semantic Distance (Cosine)', fontsize=14, fontweight='bold')

        if title is None:
            title = 'Impact of Spelling Errors on Translation Semantic Drift'
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')

        # Legend
        ax.legend(fontsize=12, loc='best')

        # Tight layout
        plt.tight_layout()

        # Save
        output_path = self.output_dir / output_file
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        print(f"\nGraph saved to: {output_path}")

        plt.close()

        return output_path

    def plot_distribution(
        self,
        df: pd.DataFrame,
        output_file: str = "distance_distribution.png"
    ) -> Path:
        """
        Plot distribution of semantic distances.

        Args:
            df: DataFrame with 'distance' column
            output_file: Output filename

        Returns:
            Path to saved graph
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Histogram
        ax.hist(df['distance'], bins=20, alpha=0.7, color='steelblue', edgecolor='black')

        ax.set_xlabel('Semantic Distance', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title('Distribution of Semantic Distances', fontsize=14, fontweight='bold', pad=15)

        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        output_path = self.output_dir / output_file
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        print(f"Distribution plot saved to: {output_path}")

        plt.close()

        return output_path

    def create_summary_statistics(self, df: pd.DataFrame) -> dict:
        """
        Calculate summary statistics.

        Args:
            df: DataFrame with analysis results

        Returns:
            Dictionary of statistics
        """
        grouped = df.groupby('error_rate')['distance'].agg([
            'count', 'mean', 'std', 'min', 'max'
        ]).round(4)

        # Overall statistics
        overall = {
            'total_cases': len(df),
            'mean_distance': df['distance'].mean(),
            'std_distance': df['distance'].std(),
            'min_distance': df['distance'].min(),
            'max_distance': df['distance'].max(),
            'correlation': df[['error_rate', 'distance']].corr().iloc[0, 1]
        }

        return {
            'by_error_rate': grouped.to_dict(),
            'overall': overall
        }
