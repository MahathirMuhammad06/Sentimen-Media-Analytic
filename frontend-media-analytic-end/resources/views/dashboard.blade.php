@extends('layouts.app')

@section('title', 'Dashboard - MEDAL')

@section('content')
<div class="min-h-screen bg-gray-50 py-8 px-8">

    {{-- Header --}}
    <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-900">
            Apa Opini Publik Hari Ini?
        </h1>
    </div>

    {{-- Search Bar --}}
    <div class="mb-8 max-w-4xl mx-auto">
        <form action="{{ route('search.results') }}" method="GET" class="relative">
            <input
                type="text"
                name="query"
                placeholder="Cari Topik (contoh: bbm, bencana alam, industri)"
                class="w-full px-6 py-4 pr-16 border border-gray-300 rounded-xl text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#2b276c] focus:border-transparent shadow-sm"
                required
            />
            <button
                type="submit"
                class="absolute right-3 top-1/2 -translate-y-1/2 bg-[#2b276c] hover:bg-[#1f1a4f] text-white px-4 py-2 rounded-lg transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
            </button>
        </form>
    </div>

    @php
        $totalArticles = ($stats['positive_count'] ?? 0) + ($stats['negative_count'] ?? 0) + ($stats['neutral_count'] ?? 0);
        
        $positifCount = $stats['positive_count'] ?? 0;
        $negatifCount = $stats['negative_count'] ?? 0;
        $netralCount = $stats['neutral_count'] ?? 0;
        
        $positifPercent = $totalArticles > 0 ? round(($positifCount / $totalArticles) * 100, 1) : 0;
        $negatifPercent = $totalArticles > 0 ? round(($negatifCount / $totalArticles) * 100, 1) : 0;
        $netralPercent = $totalArticles > 0 ? round(($netralCount / $totalArticles) * 100, 1) : 0;
    @endphp

    {{-- Sentiment Summary Cards --}}
    <div class="grid grid-cols-4 gap-4 mb-8 max-w-7xl mx-auto">
        {{-- Positif --}}
        <div class="bg-green-500 rounded-xl p-6 text-white shadow-lg">
            <div class="flex items-center justify-between mb-2">
                <span class="text-lg font-semibold">Positif</span>
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                </svg>
            </div>
            <div class="mb-1">
                <span class="text-4xl font-bold">{{ $positifCount }}</span>
                <span class="text-base font-normal ml-1">Berita</span>
            </div>
            <div class="mt-3 text-2xl font-bold">{{ $positifPercent }}%</div>
        </div>

        {{-- Negatif --}}
        <div class="bg-red-500 rounded-xl p-6 text-white shadow-lg">
            <div class="flex items-center justify-between mb-2">
                <span class="text-lg font-semibold">Negatif</span>
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"/>
                </svg>
            </div>
            <div class="mb-1">
                <span class="text-4xl font-bold">{{ $negatifCount }}</span>
                <span class="text-base font-normal ml-1">Berita</span>
            </div>
            <div class="mt-3 text-2xl font-bold">{{ $negatifPercent }}%</div>
        </div>

        {{-- Netral - DIPERBAIKI DARI bg-purple-400 MENJADI bg-yellow-500 --}}
        <div class="bg-yellow-500 rounded-xl p-6 text-white shadow-lg">
            <div class="flex items-center justify-between mb-2">
                <span class="text-lg font-semibold">Netral</span>
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14"/>
                </svg>
            </div>
            <div class="mb-1">
                <span class="text-4xl font-bold">{{ $netralCount }}</span>
                <span class="text-base font-normal ml-1">Berita</span>
            </div>
            <div class="mt-3 text-2xl font-bold">{{ $netralPercent }}%</div>
        </div>

        {{-- Total Berita --}}
        <div class="bg-gray-300 rounded-xl p-6 text-gray-800 shadow-lg">
            <div class="flex items-center justify-between mb-2">
                <span class="text-lg font-semibold">Jumlah Berita</span>
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
                </svg>
            </div>
            <div class="text-4xl font-bold">{{ $totalArticles }}</div>
        </div>
    </div>

    {{-- Chart & Table Section --}}
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8 max-w-7xl mx-auto">
        
        {{-- Horizontal Bar Chart --}}
        <div class="bg-white rounded-xl shadow-md border border-gray-200 p-6">
            <h2 class="text-xl font-bold text-gray-800 mb-4">Distribusi Sentimen</h2>
            
            <div class="mb-4 flex justify-center gap-6">
                <div class="flex items-center gap-2">
                    <div class="w-4 h-4 bg-green-500 rounded"></div>
                    <span class="text-sm font-medium text-gray-700">Positif</span>
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-4 h-4 bg-red-500 rounded"></div>
                    <span class="text-sm font-medium text-gray-700">Negatif</span>
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-4 h-4 bg-yellow-500 rounded"></div>
                    <span class="text-sm font-medium text-gray-700">Netral</span>
                </div>
            </div>

            <div style="height: 300px; position: relative;">
                <canvas id="dashboardSentimentChart"></canvas>
            </div>
        </div>

        {{-- Source Table --}}
        <div class="bg-white rounded-xl shadow-md border border-gray-200 p-6">
            <h2 class="text-xl font-bold text-gray-800 mb-4">Jumlah Berita Per Sumber</h2>
            
            <div class="overflow-y-auto" style="max-height: 350px;">
                <table class="w-full">
                    <thead class="sticky top-0 bg-gray-100 border-b-2 border-gray-300">
                        <tr>
                            <th class="text-left py-2 px-4 text-sm font-semibold text-gray-700">Sumber</th>
                            <th class="text-right py-2 px-4 text-sm font-semibold text-gray-700">Jumlah</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        @if(isset($sourcesSummary) && count($sourcesSummary) > 0)
                            @foreach($sourcesSummary as $source)
                            <tr>
                                <td class="py-3 px-4 text-sm text-gray-800">{{ $source['name'] }}</td>
                                <td class="py-3 px-4 text-sm text-gray-800 text-right font-medium">{{ $source['article_count'] }}</td>
                            </tr>
                            @endforeach
                        @else
                            <tr>
                                <td colspan="2" class="py-4 text-center text-gray-500 text-sm">Tidak ada data</td>
                            </tr>
                        @endif
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    {{-- AutoCrawler Status --}}
    <div class="grid grid-cols-4 gap-4 max-w-7xl mx-auto">
        {{-- AutoCrawler Status --}}
        <div class="bg-white rounded-xl shadow-md border border-gray-200 p-6">
            <div class="flex items-center gap-3 mb-2">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
                <h3 class="font-semibold text-gray-700">AutoCrawler Status</h3>
            </div>
            <p id="crawlerStatus" class="text-2xl font-bold text-gray-400">Loading...</p>
        </div>

        {{-- Last Crawl --}}
        <div class="bg-white rounded-xl shadow-md border border-gray-200 p-6">
            <div class="flex items-center gap-3 mb-2">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <h3 class="font-semibold text-gray-700">Last Crawl</h3>
            </div>
            <p id="lastCrawl" class="text-lg font-bold text-gray-400">Loading...</p>
        </div>

        {{-- Active Sources --}}
        <div class="bg-white rounded-xl shadow-md border border-gray-200 p-6">
            <div class="flex items-center gap-3 mb-2">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <h3 class="font-semibold text-gray-700">Active Sources</h3>
            </div>
            <p id="activeSources" class="text-2xl font-bold text-gray-400">Loading...</p>
        </div>

        {{-- Total Sources --}}
        <div class="bg-white rounded-xl shadow-md border border-gray-200 p-6">
            <div class="flex items-center gap-3 mb-2">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"/>
                </svg>
                <h3 class="font-semibold text-gray-700">Total Sources</h3>
            </div>
            <p id="totalSources" class="text-2xl font-bold text-gray-400">Loading...</p>
        </div>
    </div>

</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Chart
    const ctx = document.getElementById('dashboardSentimentChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Sentimen'],
                datasets: [
                    {
                        label: 'Positif',
                        data: [{{ $positifCount }}],
                        backgroundColor: '#22c55e',
                        borderRadius: 6,
                        barThickness: 40
                    },
                    {
                        label: 'Negatif',
                        data: [{{ $negatifCount }}],
                        backgroundColor: '#ef4444',
                        borderRadius: 6,
                        barThickness: 40
                    },
                    {
                        label: 'Netral',
                        data: [{{ $netralCount }}],
                        backgroundColor: '#eab308',
                        borderRadius: 6,
                        barThickness: 40
                    }
                ]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.x} berita`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0, 0, 0, 0.05)' },
                        ticks: { stepSize: 10 }
                    },
                    y: { grid: { display: false } }
                }
            }
        });
    }

    // Fetch AutoCrawler Status
    fetch('http://localhost:5000/v1/crawler/auto-crawl/status')
        .then(response => response.json())
        .then(data => {
            const statusEl = document.getElementById('crawlerStatus');
            const lastCrawlEl = document.getElementById('lastCrawl');
            
            if (data.auto_running) {
                statusEl.textContent = 'Active';
                statusEl.classList.remove('text-gray-400');
                statusEl.classList.add('text-green-600');
            } else {
                statusEl.textContent = 'Inactive';
                statusEl.classList.remove('text-gray-400');
                statusEl.classList.add('text-red-600');
            }
            
            if (data.last_crawl_time && data.last_crawl_time !== null) {
                const date = new Date(data.last_crawl_time);
                const formatted = date.toLocaleString('id-ID', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: false
                }).replace(',', '');
                lastCrawlEl.textContent = formatted;
                lastCrawlEl.classList.remove('text-gray-400');
                lastCrawlEl.classList.add('text-gray-800');
            } else {
                lastCrawlEl.textContent = '-';
                lastCrawlEl.classList.remove('text-gray-400');
                lastCrawlEl.classList.add('text-gray-800');
            }
        })
        .catch(error => {
            console.error('Error fetching crawler status:', error);
            document.getElementById('crawlerStatus').textContent = 'Error';
            document.getElementById('lastCrawl').textContent = 'Error';
        });

    // Fetch Sources Summary
    fetch('http://localhost:5000/v1/crawler/sources-summary')
        .then(response => response.json())
        .then(data => {
            const activeEl = document.getElementById('activeSources');
            const totalEl = document.getElementById('totalSources');
            
            activeEl.textContent = data.active_sources || 0;
            activeEl.classList.remove('text-gray-400');
            activeEl.classList.add('text-gray-800');
            
            totalEl.textContent = data.total_sources || 0;
            totalEl.classList.remove('text-gray-400');
            totalEl.classList.add('text-gray-800');
        })
        .catch(error => {
            console.error('Error fetching sources summary:', error);
            document.getElementById('activeSources').textContent = 'Error';
            document.getElementById('totalSources').textContent = 'Error';
        });
});
</script>

<x-news-detail-modal />

@endsection