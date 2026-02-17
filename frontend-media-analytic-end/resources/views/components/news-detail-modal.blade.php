{{-- News Detail Modal Component --}}

@props([
    'newsId' => null,
    'title' => 'Judul Berita',
    'source' => 'Sumber Berita',
    'content' => 'Isi berita akan ditampilkan di sini...',
    'sentiment' => 'positif',
    'isFavorite' => false,
    'sourceUrl' => '#'
])

@php
    $sentimentColors = [
        'positif' => 'bg-green-100 text-green-700 border-green-300',
        'positive' => 'bg-green-100 text-green-700 border-green-300',
        'negatif' => 'bg-red-100 text-red-700 border-red-300',
        'negative' => 'bg-red-100 text-red-700 border-red-300',
        'netral' => 'bg-yellow-100 text-yellow-700 border-yellow-300',
        'neutral' => 'bg-yellow-100 text-yellow-700 border-yellow-300'
    ];
    
    $sentimentLower = strtolower($sentiment);
    $sentimentColor = $sentimentColors[$sentimentLower] ?? 'bg-gray-100 text-gray-700 border-gray-300';
@endphp

{{-- Modal Backdrop --}}
<div id="newsDetailModal" class="hidden fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="fixed inset-0 bg-gray-900 bg-opacity-50 backdrop-blur-sm transition-opacity" onclick="closeNewsModal()"></div>

    <div class="flex min-h-full items-center justify-center p-4">
        {{-- Modal Container (50% width) --}}
        <div class="relative bg-white rounded-2xl shadow-2xl w-1/2 mx-auto transform transition-all">
            
            {{-- Close Button --}}
            <button onclick="closeNewsModal()" 
                class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors z-10">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
            </button>

            {{-- Modal Body --}}
            <div class="p-8">
                
                {{-- Judul Berita --}}
                <div class="mb-4 pr-8">
                    <h2 id="modalTitle" class="text-2xl font-bold text-gray-900 leading-tight">
                        {{ $title }}
                    </h2>
                </div>

                {{-- Sumber Berita & Favorit --}}
                <div class="flex justify-between items-start mb-6">
                    <div class="flex-1 pr-4">
                        <p id="modalSource" class="text-sm text-gray-600 font-medium">
                            {{ $source }}
                        </p>
                    </div>

                    {{-- Favorite Button --}}
                    <button id="modalFavoriteBtn" 
                        onclick="toggleModalFavorite()"
                        class="flex-shrink-0 transition-colors p-2 rounded-full hover:bg-gray-100"
                        title="Tambah ke favorit">
                        <svg class="w-7 h-7 {{ $isFavorite ? 'fill-red-500 text-red-500' : 'fill-none text-gray-400' }} hover:text-red-500" 
                             stroke="currentColor" 
                             viewBox="0 0 24 24">
                            <path stroke-width="2" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                        </svg>
                    </button>
                </div>

                {{-- Isi Berita --}}
                <div class="mb-6 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
                    <div id="modalContent" class="text-gray-700 leading-relaxed whitespace-pre-line">
                        {{ $content }}
                    </div>
                </div>

                {{-- Bottom Section --}}
                <div class="flex justify-between items-center pt-4 border-t border-gray-200">
                    {{-- Sentimen (NO EMOJI) --}}
                    <div class="flex items-center gap-3">
                        <span class="text-sm text-gray-600 font-medium">Sentimen:</span>
                        <div id="modalSentimentContainer" class="flex items-center gap-2 border px-4 py-2 rounded-lg {{ $sentimentColor }}">
                            <span id="modalSentiment" class="text-sm font-bold capitalize">{{ ucfirst($sentiment) }}</span>
                        </div>
                    </div>

                    {{-- Buka Berita Button --}}
                    <a id="modalSourceLink" 
                       href="{{ $sourceUrl }}" 
                       target="_blank" 
                       rel="noopener noreferrer"
                       class="flex items-center gap-2 bg-[#2b276c] hover:bg-[#1f1a4f] text-white px-6 py-2.5 rounded-lg font-medium transition-colors">
                        <span>Buka Berita</span>
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                        </svg>
                    </a>
                </div>

            </div>
        </div>
    </div>
</div>

<script>
let currentModalArticleId = null;

window.openNewsModal = function(newsData) {
    const modal = document.getElementById('newsDetailModal');
    
    if (newsData) {
        currentModalArticleId = newsData.newsId;
        
        document.getElementById('modalTitle').textContent = newsData.title || 'Judul Berita';
        document.getElementById('modalSource').textContent = newsData.source || 'Sumber Berita';
        document.getElementById('modalContent').textContent = newsData.content || 'Konten tidak tersedia.';
        
        const sentimentMap = {
            'positive': 'positif',
            'negative': 'negatif',
            'neutral': 'netral'
        };
        const sentiment = sentimentMap[newsData.sentiment.toLowerCase()] || newsData.sentiment.toLowerCase();
        document.getElementById('modalSentiment').textContent = sentiment.charAt(0).toUpperCase() + sentiment.slice(1);
        
        const sourceLink = document.getElementById('modalSourceLink');
        if (newsData.sourceUrl && newsData.sourceUrl !== '#') {
            sourceLink.href = newsData.sourceUrl;
        }
        
        const sentimentColors = {
            'positif': 'bg-green-100 text-green-700 border-green-300',
            'positive': 'bg-green-100 text-green-700 border-green-300',
            'negatif': 'bg-red-100 text-red-700 border-red-300',
            'negative': 'bg-red-100 text-red-700 border-red-300',
            'netral': 'bg-yellow-100 text-yellow-700 border-yellow-300',
            'neutral': 'bg-yellow-100 text-yellow-700 border-yellow-300'
        };
        
        const sentimentLower = (newsData.sentiment || 'neutral').toLowerCase();
        const container = document.getElementById('modalSentimentContainer');
        
        container.className = 'flex items-center gap-2 border px-4 py-2 rounded-lg';
        container.classList.add(...(sentimentColors[sentimentLower] || 'bg-gray-100 text-gray-700 border-gray-300').split(' '));
        
        const favoriteBtn = document.getElementById('modalFavoriteBtn');
        const favoriteSvg = favoriteBtn.querySelector('svg');
        if (newsData.isFavorite) {
            favoriteSvg.classList.remove('fill-none', 'text-gray-400');
            favoriteSvg.classList.add('fill-red-500', 'text-red-500');
            favoriteBtn.setAttribute('title', 'Hapus dari favorit');
        } else {
            favoriteSvg.classList.remove('fill-red-500', 'text-red-500');
            favoriteSvg.classList.add('fill-none', 'text-gray-400');
            favoriteBtn.setAttribute('title', 'Tambah ke favorit');
        }
    }
    
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
};

window.closeNewsModal = function() {
    const modal = document.getElementById('newsDetailModal');
    modal.classList.add('hidden');
    document.body.style.overflow = '';
    currentModalArticleId = null;
};

async function toggleModalFavorite() {
    if (!currentModalArticleId) return;
    
    try {
        const response = await fetch(`/api/favorites/${currentModalArticleId}/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]')?.content || ''
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            const btn = document.getElementById('modalFavoriteBtn');
            const svg = btn.querySelector('svg');
            
            if (data.is_favorite) {
                svg.classList.remove('fill-none', 'text-gray-400');
                svg.classList.add('fill-red-500', 'text-red-500');
                btn.setAttribute('title', 'Hapus dari favorit');
            } else {
                svg.classList.remove('fill-red-500', 'text-red-500');
                svg.classList.add('fill-none', 'text-gray-400');
                btn.setAttribute('title', 'Tambah ke favorit');
            }
            
            const customEvent = new CustomEvent('favoriteChanged', {
                detail: { articleId: currentModalArticleId, isFavorite: data.is_favorite }
            });
            document.dispatchEvent(customEvent);
            
            showToast(data.message || (data.is_favorite ? 'Berhasil ditambahkan ke favorit' : 'Berhasil dihapus dari favorit'));
            
            if (!data.is_favorite && window.location.pathname === '/favorite') {
                const card = document.querySelector(`[data-news-id="${currentModalArticleId}"]`);
                if (card) {
                    card.style.transition = 'opacity 0.3s';
                    card.style.opacity = '0';
                    setTimeout(() => {
                        card.remove();
                        const favoritesGrid = document.getElementById('favoritesGrid');
                        if (favoritesGrid && favoritesGrid.children.length === 0) {
                            location.reload();
                        }
                    }, 300);
                }
            }
        } else {
            showToast(data.message || 'Gagal mengubah status favorit', 'error');
        }
    } catch (error) {
        console.error('Error toggling favorite:', error);
        showToast('Gagal mengubah status favorit', 'error');
    }
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeNewsModal();
    }
});

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white z-50 ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.transition = 'opacity 0.3s';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
</script>

<style>
.custom-scrollbar::-webkit-scrollbar {
    width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #555;
}
</style>