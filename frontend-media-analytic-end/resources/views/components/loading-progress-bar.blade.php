{{-- Loading Progress Bar Component --}}
{{-- Usage: <x-loading-progress-bar /> --}}

<div class="bg-white border border-gray-300 rounded-xl p-4 mb-4">
    <div class="flex items-center justify-between mb-2">
        <span id="loadingText" class="text-sm font-medium text-gray-700">Mencari berita...</span>
        <span id="loadingPercent" class="text-sm font-semibold text-blue-600">0%</span>
    </div>
    
    <!-- Progress Bar -->
    <div class="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
        <div id="loadingBar" class="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-out" style="width: 0%"></div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const loadingSteps = [
        { text: 'Mencari berita...', progress: 0 },
        { text: 'Mencari berita...', progress: 25 },
        { text: 'Memproses berita...', progress: 50 },
        { text: 'Menyimpan berita...', progress: 75 },
        { text: 'Menampilkan berita...', progress: 100 }
    ];
    
    let currentStep = 0;
    const loadingText = document.getElementById('loadingText');
    const loadingPercent = document.getElementById('loadingPercent');
    const loadingBar = document.getElementById('loadingBar');
    
    function updateProgress() {
        if (currentStep < loadingSteps.length) {
            const step = loadingSteps[currentStep];
            
            loadingText.textContent = step.text;
            loadingPercent.textContent = step.progress + '%';
            loadingBar.style.width = step.progress + '%';
            
            currentStep++;
            
            // Simulate loading time
            const delay = currentStep === 1 ? 800 : 1000; // First step faster
            setTimeout(updateProgress, delay);
        } else {
            // Loading complete - you can trigger page content display here
            setTimeout(() => {
                // Hide loading screen and show content
                const loadingScreen = document.getElementById('loadingScreen');
                const mainContent = document.getElementById('mainContent');
                
                if (loadingScreen && mainContent) {
                    loadingScreen.classList.add('hidden');
                    mainContent.classList.remove('hidden');
                }
            }, 500);
        }
    }
    
    // Start loading animation
    updateProgress();
});
</script>