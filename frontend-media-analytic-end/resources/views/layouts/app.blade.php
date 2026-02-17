<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title', 'MEDAL - News Sentiment Analytic')</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body class="bg-gray-50 min-h-screen">


    
@auth
<div class="flex min-h-screen">
    
    {{-- ========================= --}}
    {{-- SIDEBAR (20% width) --}}
    {{-- ========================= --}}
    <aside class="w-1/5 bg-[#2b276c] text-white flex flex-col fixed h-screen">
        
        {{-- Logo & Title --}}
        <div class="p-6 border-b border-white/10">
            <div class="flex items-center gap-3">
                <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
                </svg>
                <div>
                    <h1 class="text-xl font-bold">MEDAL</h1>
                    <p class="text-xs text-white/70">News Sentiment Analytic</p>
                </div>
            </div>
        </div>

        {{-- Navigation Menu --}}
        <nav class="flex-1 py-6">
            <a href="{{ route('dashboard') }}" 
               class="nav-item flex items-center gap-3 px-6 py-3 transition-colors {{ request()->routeIs('dashboard') ? 'bg-white/20 border-l-4 border-white' : 'hover:bg-white/10' }}">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                </svg>
                <span class="font-medium">Dashboard</span>
            </a>

            <a href="{{ route('favorite') }}" 
               class="nav-item flex items-center gap-3 px-6 py-3 transition-colors {{ request()->routeIs('favorite') ? 'bg-white/20 border-l-4 border-white' : 'hover:bg-white/10' }}">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                </svg>
                <span class="font-medium">Favorite</span>
            </a>

            <a href="{{ route('history') }}" 
               class="nav-item flex items-center gap-3 px-6 py-3 transition-colors {{ request()->routeIs('history*') ? 'bg-white/20 border-l-4 border-white' : 'hover:bg-white/10' }}">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <span class="font-medium">History</span>
            </a>

            <a href="{{ route('master-data') }}" 
               class="nav-item flex items-center gap-3 px-6 py-3 transition-colors {{ request()->routeIs('master-data') ? 'bg-white/20 border-l-4 border-white' : 'hover:bg-white/10' }}">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"/>
                </svg>
                <span class="font-medium">Master Data</span>
            </a>
        </nav>

        {{-- Bottom Section: Settings & Profile --}}
        <div class="p-6 border-t border-white/10 space-y-4">
            
            {{-- Settings Button --}}
<div class="relative">
    <button id="settingsButton" 
            class="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-white/10 transition-colors">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        <span class="font-medium">Settings</span>
    </button>

    {{-- Settings Popup --}}
    <div id="settingsPopup" 
         class="hidden absolute bottom-full left-0 mb-2 w-80 bg-white rounded-xl shadow-2xl border border-gray-200 p-4 text-gray-800 z-50">
        
        <h3 class="font-bold text-lg mb-4 text-gray-900">Auto Crawler Settings</h3>
        
        {{-- Auto Crawler Toggle --}}
        <div class="flex items-center justify-between mb-4 pb-4 border-b border-gray-200">
            <label class="text-sm font-medium text-gray-700">Auto Crawler</label>
            <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" id="autoCrawlerToggle" class="sr-only peer">
                <div class="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
        </div>

        {{-- Scheduler Button --}}
        <div class="mb-4 pb-4 border-b border-gray-200">
            <button 
                id="schedulerButton"
                class="w-full flex items-center justify-between px-3 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg transition-colors">
                <span class="text-sm font-medium">Aktifkan Pembersihan Artikel</span>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
            </button>
            <p class="text-xs text-gray-500 mt-2">Artikel akan dihapus otomatis dalam 30 hari</p>
        </div>

        {{-- Interval Input --}}
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
                Crawler Interval (detik)
            </label>
            <input 
                type="number" 
                id="crawlerInterval" 
                min="60" 
                max="86400"
                value="3600" 
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Min. 60 detik"
            >
            <p class="text-xs text-gray-500 mt-1">Minimum 60 detik (1 menit)</p>
        </div>

        <button 
            onclick="saveSettings()" 
            class="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition-colors">
            Simpan Pengaturan
        </button>
    </div>
</div>
            {{-- Profile & Logout --}}
            <div class="flex items-center gap-3 px-4 py-3 bg-white/10 rounded-lg">
                <div class="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                    {{ strtoupper(substr(auth()->user()->name, 0, 2)) }}
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold truncate">{{ auth()->user()->name }}</p>
                    <p class="text-xs text-white/70 truncate">{{ auth()->user()->email }}</p>
                </div>
            </div>

            {{-- Logout Button --}}
            <form method="POST" action="{{ route('logout') }}">
                @csrf
                <button type="submit" 
                        class="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-red-500/20 transition-colors text-red-300 hover:text-red-200">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                    </svg>
                    <span class="font-medium">Keluar</span>
                </button>
            </form>
        </div>

    </aside>

    {{-- ========================= --}}
    {{-- MAIN CONTENT (80% width, offset by sidebar) --}}
    {{-- ========================= --}}
    <main class="flex-1 ml-[20%]">
        @yield('content')
    </main>

</div>
@endauth

{{-- Guest Layout --}}
@guest

<div class="flex min-h-screen">

    {{-- ========================= --}}
    {{-- SIDEBAR GUEST (SAMA USER) --}}
    {{-- ========================= --}}
    <aside class="w-1/5 bg-[#2b276c] text-white flex flex-col fixed h-screen">

{{-- Logo & Title --}}
<div class="p-6 border-b border-white/10">
    <div class="flex items-center gap-3">

        {{-- Icon --}}
        <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
        </svg>

        {{-- Text --}}
        <div>
            <h1 class="text-xl font-bold">MEDAL</h1>

            <div class="flex items-center gap-2 text-xs text-white/70">
                <span>News Sentiment Analytic</span>

                {{-- Badge Guest --}}
                <span class="px-2 py-0.5 bg-yellow-400/20 text-yellow-300 rounded-full text-[10px] font-semibold">
                    GUEST
                </span>
            </div>
        </div>

    </div>
</div>


        {{-- Navigation Menu --}}
        <nav class="flex-1 py-6">
            <a href="{{ route('dashboard') }}" 
               class="nav-item flex items-center gap-3 px-6 py-3 transition-colors {{ request()->routeIs('dashboard') ? 'bg-white/20 border-l-4 border-white' : 'hover:bg-white/10' }}">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                </svg>
                <span class="font-medium">Dashboard</span>
            </a>


        </nav>


        {{-- Bottom --}}
        <div class="p-6 border-t border-white/10 space-y-4">


            {{-- Login --}}
            <a href="{{ route('login') }}"
               class="w-full flex items-center gap-3 px-4 py-3 rounded-lg
                      hover:bg-white/10 transition-colors">

                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                </svg>

                <span class="font-medium">Login</span>

            </a>

        </div>

    </aside>


    {{-- ========================= --}}
    {{-- CONTENT --}}
    {{-- ========================= --}}
    <main class="flex-1 ml-[20%]">
        @yield('content')
    </main>

</div>

@endguest



<script>
document.addEventListener('DOMContentLoaded', () => {
    const settingsBtn = document.getElementById('settingsButton');
    const settingsPopup = document.getElementById('settingsPopup');
    const autoCrawlerToggle = document.getElementById('autoCrawlerToggle');
    const schedulerButton = document.getElementById('schedulerButton');

    // Toggle settings popup
    if (settingsBtn && settingsPopup) {
        settingsBtn.addEventListener('click', e => {
            e.stopPropagation();
            settingsPopup.classList.toggle('hidden');
            
            // Load current status
            if (!settingsPopup.classList.contains('hidden')) {
                loadCurrentSettings();
            }
        });

        document.addEventListener('click', e => {
            if (!settingsPopup.contains(e.target) && !settingsBtn.contains(e.target)) {
                settingsPopup.classList.add('hidden');
            }
        });
    }

    // Load current autocrawler status
    function loadCurrentSettings() {
        fetch('http://localhost:5000/v1/crawler/auto-crawl/status')
            .then(response => response.json())
            .then(data => {
                autoCrawlerToggle.checked = data.auto_running || false;
                
                if (data.interval_seconds) {
                    document.getElementById('crawlerInterval').value = data.interval_seconds;
                }
            })
            .catch(error => console.error('Error loading settings:', error));
    }

    // Auto crawler toggle handler
    if (autoCrawlerToggle) {
        autoCrawlerToggle.addEventListener('change', async function() {
            const isChecked = this.checked;
            const endpoint = isChecked 
                ? 'http://localhost:5000/v1/crawler/auto-crawl/start'
                : 'http://localhost:5000/v1/crawler/auto-crawl/stop';

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                const data = await response.json();

                if (data.status === 'started' || data.status === 'stopped') {
                    showToast(data.message || `AutoCrawler ${isChecked ? 'diaktifkan' : 'dinonaktifkan'}`);
                    
                    // Reload dashboard status
                    if (window.location.pathname === '/dashboard') {
                        location.reload();
                    }
                } else {
                    showToast('Gagal mengubah status AutoCrawler', 'error');
                    this.checked = !isChecked; // Revert
                }
            } catch (error) {
                console.error('Error toggling autocrawler:', error);
                showToast('Terjadi kesalahan', 'error');
                this.checked = !isChecked; // Revert
            }
        });
    }

    // Scheduler button handler
    if (schedulerButton) {
        schedulerButton.addEventListener('click', async function() {
            if (!confirm('Aktifkan pembersihan otomatis? History akan dihapus setiap 30 hari.')) {
                return;
            }

            try {
                const response = await fetch('http://localhost:5000/v1/cleanup/run-now?days=30', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                const data = await response.json();

                if (response.ok) {
                    showToast('Pembersihan otomatis telah diaktifkan. History akan dihapus setiap 30 hari.');
                } else {
                    showToast('Gagal mengaktifkan pembersihan otomatis', 'error');
                }
            } catch (error) {
                console.error('Error activating scheduler:', error);
                showToast('Terjadi kesalahan', 'error');
            }
        });
    }
});

// Save settings function
async function saveSettings() {
    const interval = document.getElementById('crawlerInterval').value;

    if (parseInt(interval) < 60) {
        showToast('Interval minimum adalah 60 detik', 'error');
        return;
    }

    try {
        const response = await fetch(`http://localhost:5000/v1/crawler/auto-crawl/interval?interval_seconds=${interval}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.status === 'success') {
            showToast(`Interval berhasil diubah menjadi ${interval} detik`);
            document.getElementById('settingsPopup').classList.add('hidden');

            setTimeout(() => {
                location.reload();
            }, 800);
        } else {
            showToast('Gagal mengubah interval', 'error');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        showToast('Terjadi kesalahan', 'error');
    }
}

// Toast notification
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
</html>