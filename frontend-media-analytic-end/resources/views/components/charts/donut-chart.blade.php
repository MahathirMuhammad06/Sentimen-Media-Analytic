@props([
    'data' => ['positif' => 0, 'negatif' => 0, 'netral' => 0],
    'total' => 0,
    'title' => 'Grafik Sentimen',
    'showLegend' => true,
    'chartId' => 'donutChart'
])

<div class="bg-white rounded-2xl shadow-md border border-gray-200 p-6">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">{{ $title }}</h2>

    <div class="flex justify-center">
        <div class="relative w-[320px] h-[320px]">
            <canvas id="{{ $chartId }}"></canvas>

            <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                <span class="text-4xl font-bold text-gray-800">
                    {{ $total }}
                </span>
            </div>
        </div>
    </div>

    @if($showLegend)
    <div class="flex justify-center gap-6 mt-4 text-sm">
        <div class="flex items-center gap-2">
            <span class="w-3 h-3 bg-green-500 rounded-full"></span> Positif
        </div>
        <div class="flex items-center gap-2">
            <span class="w-3 h-3 bg-red-500 rounded-full"></span> Negatif
        </div>
        <div class="flex items-center gap-2">
            <span class="w-3 h-3 bg-yellow-500 rounded-full"></span> Netral
        </div>
    </div>
    @endif
</div>

<script>
document.addEventListener('DOMContentLoaded', () => {
    if (typeof Chart === 'undefined') {
        console.error('Chart.js belum tersedia');
        return;
    }

    const canvas = document.getElementById('{{ $chartId }}');
    if (!canvas) return;

    window.__charts = window.__charts || {};

    // Destroy chart lama jika ada
    if (window.__charts['{{ $chartId }}']) {
        window.__charts['{{ $chartId }}'].destroy();
    }

    window.__charts['{{ $chartId }}'] = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: ['Positif', 'Negatif', 'Netral'],
            datasets: [{
                data: [
                    {{ $data['positif'] }},
                    {{ $data['negatif'] }},
                    {{ $data['netral'] }}
                ],
                backgroundColor: ['#22c55e', '#ef4444', '#eab308'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            cutout: '70%',
            plugins: {
                legend: { display: false }
            }
        }
    });
});
</script>
