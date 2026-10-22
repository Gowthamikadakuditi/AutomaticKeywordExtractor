/**
 * Chart.js Visualization Module
 * Renders interactive horizontal score bars and term frequency distributions.
 */

let scoresChartInstance = null;
let frequencyChartInstance = null;

function renderCharts(keywords, scoreLabel) {
    if (!keywords || keywords.length === 0) {
        return;
    }

    // Prepare labels and data (Take top 10 for clean visual charts)
    const topKeywords = keywords.slice(0, 10);
    const labels = topKeywords.map(k => k.text);
    const scores = topKeywords.map(k => k.score);
    const frequencies = topKeywords.map(k => k.frequency);

    // 1. HORIZONTAL BAR CHART - RELEVANCE SCORES
    const scoresCanvas = document.getElementById("scoresChart");
    if (scoresCanvas) {
        if (scoresChartInstance) {
            scoresChartInstance.destroy();
        }

        const ctxScores = scoresCanvas.getContext("2d");
        scoresChartInstance = new Chart(ctxScores, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: scoreLabel || "Relevance Score",
                    data: scores,
                    backgroundColor: "rgba(67, 56, 202, 0.85)", // Indigo
                    borderColor: "rgb(67, 56, 202)",
                    borderWidth: 1,
                    borderRadius: 4,
                    barPercentage: 0.7
                }]
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return ` Score: ${context.raw} (0.0 to 1.0)`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 1.0,
                        grid: {
                            color: "#f1f5f9"
                        },
                        ticks: {
                            font: { family: "'Inter', sans-serif", size: 11 }
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: { family: "'Inter', sans-serif", size: 12, weight: 500 }
                        }
                    }
                }
            }
        });
    }


    // 2. HORIZONTAL FREQUENCY CHART - OCCURRENCES
    const freqCanvas = document.getElementById("frequencyChart");

    if (freqCanvas) {
        if (frequencyChartInstance) {
            frequencyChartInstance.destroy();
        }

        const ctxFreq = freqCanvas.getContext("2d");

        frequencyChartInstance = new Chart(ctxFreq, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "In-Text Frequency",
                    data: frequencies,
                    backgroundColor: "rgba(14, 165, 233, 0.85)",
                    borderColor: "rgb(14, 165, 233)",
                    borderWidth: 1,
                    borderRadius: 4,
                    barPercentage: 0.65,
                    categoryPercentage: 0.8
                }]
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function (items) {
                                return items[0].label;
                            },
                            label: function (context) {
                                return ` Frequency: ${context.raw} times`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0,
                            stepSize: 1,
                            font: {
                                family: "'Inter', sans-serif",
                                size: 11
                            }
                        },
                        grid: {
                            color: "#f1f5f9"
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            autoSkip: false,
                            font: {
                                family: "'Inter', sans-serif",
                                size: 11
                            },
                            callback: function (value) {
                                const label = this.getLabelForValue(value);
                                return label.length > 28
                                    ? label.substring(0, 25) + "..."
                                    : label;
                            }
                        }
                    }
                }
            }
        });
    }
}