@extends('layouts.app')

@section('title', 'Detail History - MEDAL')

@section('content')
@php
    use Carbon\Carbon;
    $dt = $timestamp ? Carbon::parse($timestamp) : null;
    $persen = $sentimentStats['persen'] ?? [
        'positif' => 0,
        'negatif' => 0,
        'netral'  => 0,
    ];
    $total = ($sentimentStats['positif'] ?? 0) + ($sentimentStats['negatif'] ?? 0) + ($sentimentStats['netral'] ?? 0);
@endphp

<div class="min-h-screen bg-gray-50">
    
    {{-- Header --}}
    <div class="bg-white border-b border-gray-200 py-6">
        <div class="max-w-7xl mx-auto px-8 flex justify-between items-start">
            <div>
                <p class="text-lg font-bold text-gray-900 mb-1">Hasil Pencarian "<span class="text-[#2b276c]">{{ $query }}</span>"</p>
                <p class="text-sm text-gray-600">(data diambil dari database)</p>
            </div>
            @if ($dt)
            <div class="text-right">
                <p class="text-sm font-semibold text-gray-700">
                    {{ $dt->translatedFormat('l, d F Y') }}
                </p>
                <p class="text-xs text-gray-500">
                    {{ $dt->format('H:i') }} WIB
                </p>
            </div>
            @endif
        </div>
    </div>

    <div class="max-w-7xl mx-auto px-8 py-8">

        {{-- Sentiment Summary Cards --}}
        <div class="grid grid-cols-4 gap-4 mb-8">
            {{-- Positif --}}
            <div class="bg-green-500 rounded-xl p-6 text-white shadow-lg">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-lg font-semibold">Positif</span>
                    <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                    </svg>
                </div>
                <div class="mb-1">
                    <span class="text-4xl font-bold">{{ $sentimentStats['positif'] ?? 0 }}</span>
                    <span class="text-base ml-1 opacity-90">Berita</span>
                </div>
                <div class="mt-2 text-2xl font-bold">{{ $persen['positif'] }}%</div>
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
                    <span class="text-4xl font-bold">{{ $sentimentStats['negatif'] ?? 0 }}</span>
                    <span class="text-base ml-1 opacity-90">Berita</span>
                </div>
                <div class="mt-2 text-2xl font-bold">{{ $persen['negatif'] }}%</div>
            </div>

            {{-- Netral - WARNA DIPERBAIKI MENJADI KUNING --}}
            <div class="bg-yellow-500 rounded-xl p-6 text-white shadow-lg">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-lg font-semibold">Netral</span>
                    <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14"/>
                    </svg>
                </div>
                <div class="mb-1">
                    <span class="text-4xl font-bold">{{ $sentimentStats['netral'] ?? 0 }}</span>
                    <span class="text-base ml-1 opacity-90">Berita</span>
                </div>
                <div class="mt-2 text-2xl font-bold">{{ $persen['netral'] }}%</div>
            </div>

            {{-- Total --}}
            <div class="bg-gray-300 rounded-xl p-6 text-gray-800 shadow-lg">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-lg font-semibold">Jumlah Berita</span>
                    <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
                    </svg>
                </div>
                <div class="text-4xl font-bold">{{ $total }}</div>
            </div>
        </div>

        {{-- Chart & Table --}}
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {{-- Chart --}}
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
                    <canvas id="historyDetailChart"></canvas>
                </div>
            </div>

            {{-- Table - DATA DINAMIS --}}
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
                                        <td class="py-3 px-4 text-sm">{{ $source['name'] }}</td>
                                        <td class="py-3 px-4 text-sm text-right font-medium">{{ $source['article_count'] }}</td>
                                    </tr>
                                @endforeach
                            @else
                                <tr>
                                    <td colspan="2" class="py-4 px-4 text-sm text-center text-gray-500">
                                        Tidak ada data sumber
                                    </td>
                                </tr>
                            @endif
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        {{-- News Cards Grid (3 columns) --}}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-20">
            @forelse ($articles as $article)
                <x-news-card
                    :title="$article['title'] ?? 'Judul tidak tersedia'"
                    :source="$article['source'] ?? 'Sumber tidak diketahui'"
                    :sentiment="strtolower($article['sentiment'] ?? 'netral')"
                    :is-favorite="false"
                    :news-id="$article['id'] ?? null"
                    :content="$article['content'] ?? 'Konten tidak tersedia'"
                    :source-url="$article['url'] ?? '#'"
                />
            @empty
                <div class="col-span-3 text-center py-12">
                    <svg class="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h3 class="mt-4 text-lg font-medium text-gray-900">Tidak ada artikel</h3>
                    <p class="mt-2 text-gray-500">Tidak ditemukan artikel untuk "{{ $query }}"</p>
                </div>
            @endforelse
        </div>

        {{-- Scroll to Top --}}
        <button id="scrollToTopBtn" 
                class="hidden fixed bottom-8 right-8 bg-[#2b276c] hover:bg-[#1f1a4f] text-white p-4 rounded-full shadow-lg transition-all z-50">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/>
            </svg>
        </button>
    </div>
</div>

<x-news-detail-modal />

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Chart
    const ctx = document.getElementById('historyDetailChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Sentimen'],
                datasets: [
                    {
                        label: 'Positif',
                        data: [{{ $sentimentStats['positif'] ?? 0 }}],
                        backgroundColor: '#22c55e',
                        borderRadius: 6,
                        barThickness: 40
                    },
                    {
                        label: 'Negatif',
                        data: [{{ $sentimentStats['negatif'] ?? 0 }}],
                        backgroundColor: '#ef4444',
                        borderRadius: 6,
                        barThickness: 40
                    },
                    {
                        label: 'Netral',
                        data: [{{ $sentimentStats['netral'] ?? 0 }}],
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
                plugins: { legend: { display: false } },
                scales: {
                    x: { beginAtZero: true, grid: { color: 'rgba(0, 0, 0, 0.05)' } },
                    y: { grid: { display: false } }
                }
            }
        });
    }

    // Scroll to top
    const scrollBtn = document.getElementById('scrollToTopBtn');
    window.addEventListener('scroll', () => {
        scrollBtn.classList.toggle('hidden', window.pageYOffset <= 300);
    });
    scrollBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
</script>
@endsection