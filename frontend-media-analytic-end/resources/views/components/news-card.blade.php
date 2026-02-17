{{-- News Card Component --}}

@props([
    'title' => 'Judul Berita',
    'source' => 'Sumber Berita',
    'sentiment' => 'positif',
    'isFavorite' => false,
    'newsId' => null,
    'content' => 'Isi berita tidak tersedia.',
    'sourceUrl' => '#',
    'fullWidth' => false
])

@php
    $sentimentColors = [
        'positif' => 'bg-green-100 text-green-700 border-green-300',
        'negatif' => 'bg-red-100 text-red-700 border-red-300',
        'netral'  => 'bg-yellow-100 text-yellow-700 border-yellow-300',
        'positive' => 'bg-green-100 text-green-700 border-green-300',
        'negative' => 'bg-red-100 text-red-700 border-red-300',
        'neutral'  => 'bg-yellow-100 text-yellow-700 border-yellow-300',
    ];

    $sentimentColor = $sentimentColors[strtolower($sentiment)] ?? 'bg-gray-100 text-gray-700 border-gray-300';
    $cardId = 'news-card-' . uniqid();
    $widthClass = $fullWidth ? 'w-full' : 'w-full max-w-md';
@endphp

<div
    id="{{ $cardId }}"
    class="news-card bg-white rounded-xl border-2 border-gray-200 hover:border-[#2b276c] hover:shadow-xl transition-all cursor-pointer p-4 {{ $widthClass }}"
    data-id="{{ $newsId }}"
    data-title="{{ e($title) }}"
    data-source="{{ e($source) }}"
    data-content="{{ e($content) }}"
    data-sentiment="{{ $sentiment }}"
    data-url="{{ $sourceUrl }}"
    data-favorite="{{ $isFavorite ? 'true' : 'false' }}"
    data-news-id="{{ $newsId }}"
>
    {{-- Judul Berita --}}
    <div class="mb-3 min-h-[3rem]">
        <h3 class="font-bold text-gray-900 text-base leading-snug line-clamp-2">
            {{ $title }}
        </h3>
    </div>

    {{-- Bottom Section --}}
    <div class="flex justify-between items-center gap-3">
        {{-- Sumber Berita --}}
        <div class="flex-1 min-w-0">
            <p class="text-gray-600 text-sm truncate font-medium">{{ $source }}</p>
        </div>

        {{-- Sentimen & Favorit --}}
        <div class="flex items-center gap-2 flex-shrink-0">
            {{-- Sentiment Badge --}}
            <span class="px-3 py-1.5 rounded-lg text-xs font-bold border {{ $sentimentColor }} whitespace-nowrap">
                {{ ucfirst($sentiment) }}
            </span>

            {{-- Favorite Indicator --}}
            @if($isFavorite)
                <span class="favorite-indicator text-red-500 flex-shrink-0" data-article-id="{{ $newsId }}">
                    <svg class="w-6 h-6 fill-current" viewBox="0 0 24 24">
                        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                    </svg>
                </span>
            @endif
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const card = document.getElementById('{{ $cardId }}');
    if (card) {
        card.addEventListener('click', async function(e) {
            const newsId = this.dataset.id;
            
            if (!newsId) {
                console.error('News ID not found');
                return;
            }
            
            try {
                const response = await fetch(`/api/v1/article/${newsId}`);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (typeof openNewsModal === 'function') {
                    openNewsModal({
                        newsId: data.id,
                        title: data.title,
                        source: data.source,
                        content: data.content || 'Konten tidak tersedia.',
                        sentiment: data.sentiment,
                        sourceUrl: data.url,
                        isFavorite: data.is_favorite || false
                    });
                }
                
            } catch (error) {
                console.error('Error fetching article:', error);
                
                if (typeof openNewsModal === 'function') {
                    openNewsModal({
                        newsId: this.dataset.id,
                        title: this.dataset.title,
                        source: this.dataset.source,
                        content: this.dataset.content || 'Gagal memuat konten berita.',
                        sentiment: this.dataset.sentiment,
                        sourceUrl: this.dataset.url,
                        isFavorite: this.dataset.favorite === 'true'
                    });
                }
            }
        });
    }
});

// Listen for favorite changes
document.addEventListener('favoriteChanged', function(e) {
    const { articleId, isFavorite } = e.detail;
    const card = document.querySelector(`[data-news-id="${articleId}"]`);
    
    if (card) {
        card.setAttribute('data-favorite', isFavorite ? 'true' : 'false');
        
        const existingIndicator = card.querySelector('.favorite-indicator');
        
        if (isFavorite && !existingIndicator) {
            const sentimentBadge = card.querySelector('.flex.items-center.gap-2');
            if (sentimentBadge) {
                const heartHTML = `
                    <span class="favorite-indicator text-red-500 flex-shrink-0" data-article-id="${articleId}">
                        <svg class="w-6 h-6 fill-current" viewBox="0 0 24 24">
                            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                        </svg>
                    </span>
                `;
                sentimentBadge.insertAdjacentHTML('beforeend', heartHTML);
            }
        } else if (!isFavorite && existingIndicator) {
            existingIndicator.remove();
        }
    }
});
</script>

<style>
.line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>