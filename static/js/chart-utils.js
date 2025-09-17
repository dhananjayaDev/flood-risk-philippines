// Chart Utilities Module

// Tooltip Style Presets
const TOOLTIP_STYLES = {
    glassmorphism: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1,
        borderRadius: 6,
        padding: 8
    },
    minimal: {
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        titleColor: '#333',
        bodyColor: '#666',
        borderColor: 'rgba(0, 0, 0, 0.1)',
        borderWidth: 1,
        borderRadius: 8,
        padding: 12
    },
    darkModern: {
        backgroundColor: 'rgba(20, 20, 20, 0.95)',
        titleColor: '#fff',
        bodyColor: '#ccc',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 0,
        borderRadius: 12,
        padding: 10
    },
    coloredAccent: {
        backgroundColor: 'rgba(59, 130, 246, 0.95)',
        titleColor: 'white',
        bodyColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 0,
        borderRadius: 8,
        padding: 10
    },
    subtleGlass: {
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        titleColor: 'white',
        bodyColor: 'rgba(255, 255, 255, 0.8)',
        borderColor: 'rgba(255, 255, 255, 0.3)',
        borderWidth: 1,
        borderRadius: 10,
        padding: 8
    }
};

// Function to get tooltip configuration
function getTooltipConfig(style = 'glassmorphism') {
    const baseConfig = {
        enabled: true,
        displayColors: false,
        position: 'nearest',
        xAlign: 'center',
        yAlign: 'bottom',
        caretSize: 4,
        cornerRadius: 8,
        titleSpacing: 4,
        titleMarginBottom: 6,
        bodySpacing: 4,
        usePointStyle: false,
        rtl: false,
        textDirection: 'ltr',
        animation: {
            duration: 200,
            easing: 'easeOutQuart'
        },
        filter: function(tooltipItem) {
            return true;
        },
        titleFont: {
            family: 'Segoe UI, -apple-system, BlinkMacSystemFont, Inter, Roboto, sans-serif',
            size: 10,
            weight: 500
        },
        bodyFont: {
            family: 'Segoe UI, -apple-system, BlinkMacSystemFont, Inter, Roboto, sans-serif',
            size: 9,
            weight: 400
        },
        callbacks: {
            title: function(context) {
                const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
                return days[context[0].dataIndex];
            },
            label: function(context) {
                return `Height: ${context.parsed.y}m`;
            }
        }
    };
    
    return { ...baseConfig, ...TOOLTIP_STYLES[style] };
}

// Demo function to change tooltip style (for testing)
function changeTooltipStyle(style) {
    if (window.riverHeightChart && TOOLTIP_STYLES[style]) {
        window.riverHeightChart.options.plugins.tooltip = getTooltipConfig(style);
        window.riverHeightChart.update();
        console.log(`Tooltip style changed to: ${style}`);
    } else {
        console.log('Available styles:', Object.keys(TOOLTIP_STYLES));
    }
}

// Make functions globally available for testing
window.changeTooltipStyle = changeTooltipStyle;
window.TOOLTIP_STYLES = TOOLTIP_STYLES;

// Initialize Weather Charts
function initWeatherCharts(astronomyData = null) {
    // Wind Line Chart
    const windLineCtx = document.getElementById('windLineChart').getContext('2d');
    new Chart(windLineCtx, {
        type: 'line',
        data: {
            labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
            datasets: [{
                data: [5.2, 6.8, 7.9, 8.1, 7.3, 6.5],
                borderColor: 'rgba(255,255,255,0.8)',
                backgroundColor: 'transparent',
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { display: false },
                y: { display: false }
            }
        }
    });

    // Wind Bar Chart
    const windBarCtx = document.getElementById('windBarChart').getContext('2d');
    new Chart(windBarCtx, {
        type: 'bar',
        data: {
            labels: ['1', '2', '3', '4', '5', '6', '7', '8'],
            datasets: [{
                data: [3, 5, 4, 7, 6, 8, 5, 4],
                backgroundColor: 'rgba(255,255,255,0.3)',
                borderColor: 'rgba(255,255,255,0.5)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { display: false },
                y: { display: false }
            }
        }
    });

    // Sun Line Chart (Sunrise/Sunset)
    const sunArcCtx = document.getElementById('sunArcChart').getContext('2d');
    
    // Get sunrise and sunset times from astronomy data or use defaults
    const sunriseTime = astronomyData && astronomyData.sunrise ? astronomyData.sunrise : '06:00 AM';
    const sunsetTime = astronomyData && astronomyData.sunset ? astronomyData.sunset : '06:00 PM';
    
    new Chart(sunArcCtx, {
        type: 'line',
        data: {
            labels: [sunriseTime, sunsetTime],
            datasets: [{
                data: [0, 0], // Same y-value to create a straight horizontal line
                borderColor: 'rgba(255,255,255,0.8)',
                backgroundColor: 'transparent',
                borderWidth: 2,
                pointRadius: 4,
                pointBackgroundColor: 'rgba(255,255,255,0.9)',
                pointBorderColor: 'rgba(255,255,255,0.5)',
                pointBorderWidth: 1,
                tension: 0, // No curve, straight line
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { display: false },
                tooltip: {
                    enabled: true,
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            return context.label === sunriseTime ? sunriseTime : sunsetTime;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: 'rgba(255,255,255,0.8)',
                        font: {
                            size: 10,
                            family: 'Segoe UI, -apple-system, BlinkMacSystemFont, Inter, Roboto, sans-serif'
                        }
                    }
                },
                y: {
                    display: false
                }
            },
            elements: {
                point: {
                    hoverRadius: 6
                }
            }
        }
    });
}

// Initialize River Height Chart
function initRiverHeightChart(riverData = null) {
    const ctx = document.getElementById('riverHeightChart').getContext('2d');
    
    // Use 7-day data if available, otherwise use fallback
    let labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']; // Fallback labels
    let data = [0, 0, 0, 2.5, 0, 0, 0]; // Fallback: zeros with current day height
    
    if (riverData && Array.isArray(riverData)) {
        // Use dynamic day names from the data
        labels = riverData.map(day => day.day);
        data = riverData.map(day => day.height);
    }
    
    const riverHeightChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'River Height (m)',
                data: data,
                borderColor: 'rgba(255, 255, 255, 0.7)',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(255, 255, 255, 0.9)',
                pointBorderColor: 'rgba(255, 255, 255, 0.5)',
                pointBorderWidth: 1,
                pointRadius: 3,
                pointHoverRadius: 5,
                pointHoverBackgroundColor: 'rgba(255, 255, 255, 1)',
                pointHoverBorderColor: 'rgba(255, 255, 255, 0.7)',
                pointHoverBorderWidth: 2,
                tension: 0.4,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    top: 20,
                    bottom: 5,
                    left: 15,
                    right: 15
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                // Change tooltip style here: 'glassmorphism', 'minimal', 'darkModern', 'coloredAccent', 'subtleGlass'
                tooltip: getTooltipConfig('glassmorphism')
            },
            scales: {
                x: {
                    display: false
                },
                y: {
                    display: false
                }
            },
            elements: {
                point: {
                    hoverBackgroundColor: 'rgba(255, 255, 255, 1)'
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            animation: {
                duration: 2000,
                easing: 'easeInOutQuart',
                onComplete: function() {
                    // Add custom labels after chart is drawn
                    addCustomLabels(riverHeightChart);
                }
            },
            transitions: {
                show: {
                    animations: {
                        x: {
                            from: 0
                        },
                        y: {
                            from: 0
                        }
                    }
                },
                hide: {
                    animations: {
                        x: {
                            to: 0
                        },
                        y: {
                            to: 0
                        }
                    }
                }
            }
        }
    });
    
    // Make chart globally accessible for tooltip style changes
    window.riverHeightChart = riverHeightChart;
}

// Add custom labels to charts
function addCustomLabels(chart) {
    const ctx = chart.ctx;
    const data = chart.data.datasets[0].data;
    const meta = chart.getDatasetMeta(0);
    const chartArea = chart.chartArea;
    
    ctx.save();
    ctx.font = '10px Segoe UI, -apple-system, BlinkMacSystemFont, Inter, Roboto, sans-serif';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.textBaseline = 'top';
    
    meta.data.forEach((point, index) => {
        const x = point.x;
        let y = point.y + 25; // Position below the point with more spacing
        
        // Ensure labels don't go below the chart area
        if (y > chartArea.bottom - 30) {
            y = chartArea.bottom - 30;
        }
        
        // Adjust text alignment for edge points
        if (index === 0) {
            ctx.textAlign = 'left';
        } else if (index === data.length - 1) {
            ctx.textAlign = 'right';
        } else {
            ctx.textAlign = 'center';
        }
        
        ctx.fillText(data[index] + 'm', x, y);
    });
    
    ctx.restore();
}
