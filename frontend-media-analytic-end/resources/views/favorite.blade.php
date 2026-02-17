@extends('layouts.app')

@section('title', 'Favorite - MEDAL')

@section('content')
<div class="min-h-screen bg-gray-50 py-8 px-8">

    {{-- Header --}}
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-800">Berita Favorit</h1>
        <p class="text-gray-600 mt-2">Daftar berita yang telah Anda tandai sebagai favorit</p>
    </div>

    {{-- Grid Cards (4 columns) --}}
    <div id="favoritesGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 pb-20">
        @if(!empty($favorites) && count($favorites) > 0)
            @foreach($favorites as $favorite)
                @php
                    $article = $favorite['article'] ?? $favorite;
                    $articleId = $favorite['article_id'] ?? ($article['id'] ?? null);
                @endphp

                @if($article && isset($article['title']))
                    <x-news-card
                        :title="$article['title'] ?? 'Judul tidak tersedia'"
                        :source="$article['source'] ?? 'Sumber tidak diketahui'"
                        :sentiment="$article['sentiment'] ?? 'netral'"
                        :news-id="$articleId"
                        :is-favorite="true"
                        :content="$article['content'] ?? 'Konten tidak tersedia'"
                        :source-url="$article['url'] ?? '#'"
                        :full-width="true"
                    />
                @endif
            @endforeach
        @else
            {{-- Empty State --}}
            <div class="col-span-4 text-center py-16">
                <svg class="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                </svg>
                <h3 class="mt-4 text-lg font-semibold text-gray-900">Belum ada favorit</h3>
                <p class="mt-2 text-gray-500">Klik ikon ❤️ di modal berita untuk menambah favorit</p>
                <a href="{{ route('dashboard') }}"
                   class="inline-block mt-6 px-6 py-2 bg-[#2b276c] text-white rounded-lg hover:bg-[#1f1a4f] transition">
                    Jelajahi Berita
                </a>
            </div>
        @endif
    </div>

    {{-- Scroll to Top --}}
    <button id="scrollToTopBtn" 
            class="hidden fixed bottom-8 right-8 bg-[#2b276c] hover:bg-[#1f1a4f] text-white p-4 rounded-full shadow-lg transition-all z-50">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/>
        </svg>
    </button>
</div>

<x-news-detail-modal />

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Scroll to top
    const scrollBtn = document.getElementById('scrollToTopBtn');
    window.addEventListener('scroll', () => {
        scrollBtn.classList.toggle('hidden', window.pageYOffset <= 300);
    });
    scrollBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Listen for favorite changes
    document.addEventListener('favoriteChanged', function(e) {
        const { articleId, isFavorite } = e.detail;
        if (!isFavorite) {
            const card = document.querySelector(`[data-news-id="${articleId}"]`);
            if (card) {
                card.style.transition = 'opacity 0.3s';
                card.style.opacity = '0';
                setTimeout(() => {
                    card.remove();
                    const grid = document.getElementById('favoritesGrid');
                    if (grid && grid.children.length === 0) {
                        location.reload();
                    }
                }, 300);
            }
        }
    });
});
</script>
@endsection