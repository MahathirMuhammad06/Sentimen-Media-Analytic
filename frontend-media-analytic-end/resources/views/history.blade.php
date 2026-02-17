@extends('layouts.app')

@section('title', 'History - MEDAL')

@section('content')
<div class="min-h-screen bg-gray-50 py-8 px-8">

    {{-- Search --}}
    <div class="flex justify-center mb-6">
        <div class="relative w-full max-w-2xl">
            <span class="absolute inset-y-0 left-4 flex items-center text-gray-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
            </span>
            <input
                type="text"
                id="searchInput"
                placeholder="Cari Topik (contoh: bbm, bencana alam, industri)"
                class="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-300 bg-white
                       focus:outline-none focus:ring-2 focus:ring-[#2b276c]"
            >
        </div>
    </div>

    {{-- Sort & Clear --}}
    <div class="flex justify-between items-center mb-8">
        <div class="flex items-center gap-3">
            <span class="text-gray-700 font-medium">Urutkan berdasarkan:</span>
            <div class="relative">
                <button id="sortDropdownButton"
                    class="flex items-center gap-2 px-6 py-2 rounded-full bg-white border
                           border-gray-300 text-sm font-medium hover:bg-gray-50 transition">
                    <span id="sortDropdownText">Terbaru</span>
                    <svg id="dropdownArrow" class="w-4 h-4 text-gray-600 transition-transform"
                         fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                    </svg>
                </button>
                <div id="sortDropdownMenu"
                     class="hidden absolute top-full mt-2 w-full bg-white border border-gray-300
                            rounded-xl shadow-lg z-10">
                    <button data-sort="desc"
                            class="sort-option w-full px-4 py-2.5 text-left text-sm hover:bg-blue-50 rounded-t-xl">
                        Terbaru
                    </button>
                    <button data-sort="asc"
                            class="sort-option w-full px-4 py-2.5 text-left text-sm hover:bg-blue-50 border-t rounded-b-xl">
                        Terlama
                    </button>
                </div>
            </div>
        </div>

        @if(!empty($history) && count($history) > 0)
        <button id="clearAllBtn" onclick="clearAllHistory()"
                class="px-4 py-2 rounded-lg bg-red-500 text-white text-sm font-medium hover:bg-red-600 transition">
            <div class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
                <span>Hapus Semua</span>
            </div>
        </button>
        @endif
    </div>

    {{-- History List --}}
    <div id="historyList" class="space-y-4">
        @forelse ($history as $item)
            @php
                $dt = \Carbon\Carbon::parse($item['created_at']);
            @endphp
            <x-history-item
                :date="$dt->translatedFormat('l, d F Y')"
                :time="$dt->format('H:i')"
                :query="$item['keyword']"
                :timestamp="$item['created_at']"
                :history-id="$item['id']"
            />
        @empty
            <div class="text-center py-12 text-gray-500">
                <svg class="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <p class="text-lg font-medium">Belum ada riwayat pencarian</p>
                <p class="text-sm text-gray-400 mt-2">Pencarian Anda akan muncul di sini</p>
            </div>
        @endforelse
    </div>
</div>

<script>
const dropdownButton = document.getElementById('sortDropdownButton');
const dropdownMenu = document.getElementById('sortDropdownMenu');
const dropdownText = document.getElementById('sortDropdownText');
const dropdownArrow = document.getElementById('dropdownArrow');
const historyList = document.getElementById('historyList');
const searchInput = document.getElementById('searchInput');

let items = Array.from(document.querySelectorAll('.history-item'));

dropdownButton?.addEventListener('click', e => {
    e.stopPropagation();
    dropdownMenu.classList.toggle('hidden');
    dropdownArrow.classList.toggle('rotate-180');
});

document.addEventListener('click', () => {
    dropdownMenu?.classList.add('hidden');
    dropdownArrow?.classList.remove('rotate-180');
});

document.querySelectorAll('.sort-option').forEach(option => {
    option.addEventListener('click', () => {
        dropdownText.textContent = option.textContent;
        sortItems(option.dataset.sort);
        dropdownMenu.classList.add('hidden');
        dropdownArrow.classList.remove('rotate-180');
    });
});

function sortItems(order) {
    items = Array.from(document.querySelectorAll('.history-item'));
    items.sort((a, b) => {
        const dateA = new Date(a.dataset.date);
        const dateB = new Date(b.dataset.date);
        return order === 'asc' ? dateA - dateB : dateB - dateA;
    });
    historyList.innerHTML = '';
    items.forEach(item => historyList.appendChild(item));
}

searchInput?.addEventListener('input', e => {
    const query = e.target.value.toLowerCase();
    items = Array.from(document.querySelectorAll('.history-item'));
    items.forEach(item => {
        item.style.display = item.textContent.toLowerCase().includes(query) ? 'block' : 'none';
    });
});

window.clearAllHistory = async function() {
    if (!confirm('Hapus semua riwayat pencarian?')) return;
    try {
        const response = await fetch('/api/history', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]')?.content || ''
            }
        });
        const data = await response.json();
        if (data.success) {
            location.reload();
        }
    } catch (error) {
        console.error('Error:', error);
    }
};

document.addEventListener('DOMContentLoaded', () => sortItems('desc'));
</script>

<style>
.rotate-180 { transform: rotate(180deg); }
</style>
@endsection