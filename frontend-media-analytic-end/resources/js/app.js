import Chart from 'chart.js/auto';
window.Chart = Chart;

import './bootstrap';
import Alpine from 'alpinejs';
window.Alpine = Alpine;
Alpine.start();

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('canvas[data-positif]').forEach(canvas => {
        const positif = Number(canvas.dataset.positif);
        const negatif = Number(canvas.dataset.negatif);
        const netral  = Number(canvas.dataset.netral);

        new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: ['Positif', 'Negatif', 'Netral'],
                datasets: [{
                    data: [positif, negatif, netral],
                    backgroundColor: ['#22c55e', '#ef4444', '#eab308'],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '70%',
                plugins: {
                    legend: { display: false }
                }
            }
        });
    });
});

