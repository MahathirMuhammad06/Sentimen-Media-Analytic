{{-- History Item Component with Delete Button --}}
{{-- Usage: <x-history-item date="Jum'at, 09 Januari 2026" time="10.52" query="Sawit" :timestamp="$timestamp" :historyId="$id" /> --}}

@props([
    'date' => '',
    'time' => '',
    'query' => '',
    'timestamp' => '', // ISO format for sorting: 2026-01-09T10:52
    'historyId' => null, // ID untuk delete
    'url' => null // Optional custom URL, default to dashboard with query
])

@php
    use Carbon\Carbon;
    
    // Parse timestamp untuk mendapatkan tanggal dan waktu yang benar
    $dt = null;
    if ($timestamp) {
        try {
            $dt = Carbon::parse($timestamp);
            $date = $dt->translatedFormat('l, d F Y'); // Format: Jum'at, 09 Januari 2026
            $time = $dt->format('H:i'); // Format: 10:52
        } catch (\Exception $e) {
            // Jika parsing gagal, gunakan nilai default dari props
        }
    }
    
    // Default URL: history detail page
    $redirectUrl = $url ?? route('history.detail', ['query' => $query, 'timestamp' => $timestamp]);
@endphp

<div class="history-item bg-white border border-gray-300 rounded-xl px-6 py-4 hover:shadow-lg hover:border-blue-400 transition-all"
     data-date="{{ $timestamp }}"
     data-history-id="{{ $historyId }}">
    
    <div class="flex justify-between items-center gap-4">
        <!-- Left Side: Date & Time -->
        <div class="flex flex-col flex-shrink-0">
            <p class="text-sm font-semibold text-gray-800">{{ $date }}</p>
            <p class="text-xs text-gray-500 mt-0.5">{{ $time }}</p>
        </div>
        
        <!-- Middle: Search Query (Clickable) -->
        <a href="{{ $redirectUrl }}" 
           class="flex-1 flex items-center gap-2 group cursor-pointer min-w-0">
            <p class="text-sm text-gray-700 group-hover:text-blue-600 transition-colors truncate">
                Anda mencari <span class="font-semibold text-gray-900 group-hover:text-blue-700">"{{ $query }}"</span>
            </p>
            <!-- Arrow Icon -->
            <svg class="w-5 h-5 text-gray-400 group-hover:text-blue-600 transition-colors flex-shrink-0" 
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
        </a>

        <!-- Right Side: Delete Button -->
        <button onclick="deleteHistory({{ $historyId }}, event)" 
                class="delete-btn flex-shrink-0 p-2 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-all"
                title="Hapus history"
                type="button">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
        </button>
    </div>
</div>

<script>
// Global function to delete history (only define once)
if (typeof window.deleteHistory === 'undefined') {
    window.deleteHistory = async function(historyId, event) {
        event.stopPropagation();
        event.preventDefault();
        
        // Confirmation
        if (!confirm('Hapus history pencarian ini?')) {
            return;
        }
        
        const historyItem = document.querySelector(`[data-history-id="${historyId}"]`);
        
        try {
            const response = await fetch(`/api/history/${historyId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]')?.content || ''
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Fade out animation
                if (historyItem) {
                    historyItem.style.transition = 'opacity 0.3s, transform 0.3s';
                    historyItem.style.opacity = '0';
                    historyItem.style.transform = 'translateX(20px)';
                    
                    setTimeout(() => {
                        historyItem.remove();
                        
                        // Check if history list is empty
                        const historyList = document.getElementById('historyList');
                        if (historyList) {
                            const remainingItems = historyList.querySelectorAll('.history-item');
                            
                            if (remainingItems.length === 0) {
                                historyList.innerHTML = `
                                    <div class="text-center py-12 text-gray-500">
                                        <svg class="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                        </svg>
                                        <p class="text-lg font-medium">Belum ada riwayat pencarian</p>
                                        <p class="text-sm text-gray-400 mt-2">Pencarian Anda akan muncul di sini</p>
                                    </div>
                                `;
                                
                                // Hide clear all button if exists
                                const clearAllBtn = document.getElementById('clearAllBtn');
                                if (clearAllBtn) {
                                    clearAllBtn.style.display = 'none';
                                }
                            }
                        }
                    }, 300);
                }
                
                // Show toast
                if (typeof showToast === 'function') {
                    showToast(data.message || 'History berhasil dihapus');
                }
            } else {
                if (typeof showToast === 'function') {
                    showToast(data.message || 'Gagal menghapus history', 'error');
                }
            }
        } catch (error) {
            console.error('Error deleting history:', error);
            if (typeof showToast === 'function') {
                showToast('Gagal menghapus history', 'error');
            }
        }
    };
}

// Toast notification function (if not already defined)
if (typeof window.showToast === 'undefined') {
    window.showToast = function(message, type = 'success') {
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
    };
}
</script>