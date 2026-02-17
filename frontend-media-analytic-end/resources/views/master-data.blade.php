@extends('layouts.app')

@section('title', 'Master Data - MEDAL')

@section('content')
<div class="min-h-screen bg-gray-50 py-8 px-8">
    
    {{-- Header --}}
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-800">Master Data</h1>
        <p class="text-gray-600 mt-1">Kelola data sumber berita untuk sistem crawling</p>
    </div>

    {{-- Form Tambah Sumber --}}
    <div class="max-w-5xl mx-auto mb-8">
        <div class="bg-white rounded-xl shadow-md border border-gray-200 p-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-6">Tambah Sumber Berita Baru</h2>
            
            <form id="addSourceForm" class="space-y-4">
                @csrf
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {{-- Nama Sumber --}}
                    <div>
                        <label for="nama_sumber" class="block text-sm font-medium text-gray-700 mb-2">
                            Nama Sumber
                        </label>
                        <input 
                            type="text" 
                            id="nama_sumber" 
                            name="nama_sumber"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#2b276c] focus:border-transparent transition"
                            placeholder="Contoh: Kompas"
                            required
                        >
                    </div>

                    {{-- Alamat Domain --}}
                    <div>
                        <label for="alamat_domain" class="block text-sm font-medium text-gray-700 mb-2">
                            Alamat Domain
                        </label>
                        <input 
                            type="url" 
                            id="alamat_domain" 
                            name="alamat_domain"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#2b276c] focus:border-transparent transition"
                            placeholder="https://www.kompas.com"
                            required
                        >
                    </div>
                </div>

                {{-- Tombol Tambah --}}
                <div class="flex justify-start pt-2">
                    <button 
                        type="submit"
                        id="submitBtn"
                        class="inline-flex items-center px-6 py-3 bg-[#2b276c] hover:bg-[#1f1a4f] text-white font-medium rounded-lg transition shadow-sm"
                    >
                        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                        </svg>
                        Tambahkan Sumber
                    </button>
                </div>
            </form>
        </div>
    </div>

    {{-- Tabel Data Sumber --}}
    <div class="max-w-5xl mx-auto">
        <div class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-[#2b276c] text-white">
                        <tr>
                            <th class="px-6 py-4 text-left text-sm font-semibold">Nama Sumber</th>
                            <th class="px-6 py-4 text-left text-sm font-semibold">Alamat Domain</th>
                            <th class="px-6 py-4 text-center text-sm font-semibold w-32">Aksi</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody" class="divide-y divide-gray-200">
                        @if(isset($sources) && count($sources) > 0)
                            @foreach($sources as $source)
                                <tr class="hover:bg-gray-50 transition" data-source-id="{{ $source['id'] }}">
                                    <td class="px-6 py-4 text-sm text-gray-800 font-medium">{{ $source['name'] }}</td>
                                    <td class="px-6 py-4 text-sm text-blue-600">
                                        <a href="{{ $source['base_url'] }}" target="_blank" class="hover:underline">
                                            {{ $source['base_url'] }}
                                        </a>
                                    </td>
                                    <td class="px-6 py-4 text-center">
                                        <button 
                                            onclick="deleteSource({{ $source['id'] }})" 
                                            class="inline-flex items-center gap-1 px-3 py-1.5 bg-red-500 hover:bg-red-600 text-white text-sm font-medium rounded-lg transition"
                                            title="Hapus">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                            </svg>
                                            Hapus
                                        </button>
                                    </td>
                                </tr>
                            @endforeach
                        @else
                            <tr>
                                <td colspan="3" class="px-6 py-8 text-center text-gray-500">
                                    Belum ada sumber berita
                                </td>
                            </tr>
                        @endif
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    {{-- Scroll to Top --}}
    <button 
        id="scrollToTop"
        class="fixed bottom-8 right-8 bg-[#2b276c] hover:bg-[#1f1a4f] text-white p-3 rounded-full shadow-lg transition opacity-0 invisible"
    >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path>
        </svg>
    </button>
</div>

<script>
    // Scroll to top
    const scrollToTopBtn = document.getElementById('scrollToTop');
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollToTopBtn.classList.remove('opacity-0', 'invisible');
            scrollToTopBtn.classList.add('opacity-100', 'visible');
        } else {
            scrollToTopBtn.classList.add('opacity-0', 'invisible');
            scrollToTopBtn.classList.remove('opacity-100', 'visible');
        }
    });
    scrollToTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Form submission
    document.getElementById('addSourceForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const namaSumber = document.getElementById('nama_sumber').value;
        const alamatDomain = document.getElementById('alamat_domain').value;
        const submitBtn = document.getElementById('submitBtn');
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Menambahkan...';
        
        try {
            const response = await fetch('{{ route("sources.store") }}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': '{{ csrf_token() }}'
                },
                body: JSON.stringify({
                    name: namaSumber,
                    base_url: alamatDomain
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('Sumber berhasil ditambahkan!');
                location.reload();
            } else {
                alert('Gagal menambahkan sumber: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Terjadi kesalahan saat menambahkan sumber');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg> Tambahkan Sumber';
        }
    });

    // Delete source
    async function deleteSource(sourceId) {
        if (!confirm('Apakah Anda yakin ingin menghapus sumber berita ini?')) return;
        
        try {
            const response = await fetch(`/api/sources/${sourceId}`, {
                method: 'DELETE',
                headers: { 'X-CSRF-TOKEN': '{{ csrf_token() }}' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('Sumber berhasil dihapus!');
                const row = document.querySelector(`tr[data-source-id="${sourceId}"]`);
                if (row) {
                    row.style.transition = 'opacity 0.3s';
                    row.style.opacity = '0';
                    setTimeout(() => row.remove(), 300);
                }
            } else {
                alert('Gagal menghapus sumber: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Terjadi kesalahan saat menghapus sumber');
        }
    }
</script>
@endsection