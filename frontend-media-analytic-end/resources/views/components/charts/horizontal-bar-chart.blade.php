{{-- Horizontal Bar Chart Component --}}
{{-- Usage: <x-charts.horizontal-bar-chart :data="$sentimentByCategory" title="Sentimen per Kategori" /> --}}

@props([
    'data' => [
        ['label' => 'Politik', 'positif' => 30, 'negatif' => 10, 'netral' => 5],
        ['label' => 'Ekonomi', 'positif' => 25, 'negatif' => 8, 'netral' => 7],
        ['label' => 'Olahraga', 'positif' => 40, 'negatif' => 5, 'netral' => 3],
        ['label' => 'Teknologi', 'positif' => 37, 'negatif' => 11, 'netral' => 10]
    ],
    'title' => 'Sentimen per Kategori',
    'showLegend' => true,
    'chartId' => 'horizontalBarChart', // Unique ID for multiple charts
    'height' => '400px'
])

@php
    // Extract labels and data
    $labels = array_column($data, 'label');
    $positifData = array_column($data, 'positif');
    $negatifData = array_column($data, 'negatif');
    $netralData = array_column($data, 'netral');
@endphp

<div class="bg-white rounded-2xl shadow-md border border-gray-200 p-8">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">{{ $title }}</h2>
    
    @if($showLegend)
    <!-- Legend -->
    <div class="flex justify-center gap-6 mb-4">
        <div class="flex items-center gap-2">
            <div class="w-4 h-4 bg-green-500 rounded"></div>
            <span class="text-sm text-gray-700 font-medium">Positif</span>
        </div>
        <div class="flex items-center gap-2">
            <div class="w-4 h-4 bg-red-500 rounded"></div>
            <span class="text-sm text-gray-700 font-medium">Negatif</span>
        </div>
        <div class="flex items-center gap-2">
            <div class="w-4 h-4 bg-yellow-500 rounded"></div>
            <span class="text-sm text-gray-700 font-medium">Netral</span>
        </div>
    </div>
    @endif
    
    <!-- Chart Container -->
    <div style="height: {{ $height }}; position: relative;">
        <canvas id="{{ $chartId }}"></canvas>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('{{ $chartId }}');
    
    if (ctx) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: @json($labels),
                datasets: [
                    {
                        label: 'Positif',
                        data: @json($positifData),
                        backgroundColor: '#22c55e', // green-500
                        borderRadius: 6,
                        barThickness: 20,
                        maxBarThickness: 30
                    },
                    {
                        label: 'Negatif',
                        data: @json($negatifData),
                        backgroundColor: '#ef4444', // red-500
                        borderRadius: 6,
                        barThickness: 20,
                        maxBarThickness: 30
                    },
                    {
                        label: 'Netral',
                        data: @json($netralData),
                        backgroundColor: '#eab308', // yellow-500
                        borderRadius: 6,
                        barThickness: 20,
                        maxBarThickness: 30
                    }
                ]
            },
            options: {
                indexAxis: 'y', // Horizontal bar
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false // We have custom legend
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {
                            size: 14,
                            weight: 'bold'
                        },
                        bodyFont: {
                            size: 13
                        },
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const value = context.parsed.x || 0;
                                return `${label}: ${value} berita`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        stacked: false,
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            stepSize: 10,
                            font: {
                                size: 12
                            }
                        },
                        title: {
                            display: true,
                            text: 'Jumlah Berita',
                            font: {
                                size: 13,
                                weight: 'bold'
                            }
                        }
                    },
                    y: {
                        stacked: false,
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 13,
                                weight: '500'
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }
});
</script>