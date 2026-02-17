{{-- Skeleton Loader Components --}}

{{-- Skeleton for Header (History Detail) --}}
@props(['type' => 'header'])

@if($type === 'header')
<div class="animate-pulse">
    <div class="flex items-center justify-between">
        <div class="flex-1">
            <div class="h-4 bg-gray-300 rounded w-40 mb-2"></div>
            <div class="h-8 bg-gray-300 rounded w-32"></div>
        </div>
        <div class="text-right">
            <div class="h-4 bg-gray-300 rounded w-48 mb-1"></div>
            <div class="h-3 bg-gray-300 rounded w-24"></div>
        </div>
    </div>
</div>
@endif

{{-- Skeleton for Chart --}}
@if($type === 'chart')
<div class="bg-white rounded-2xl shadow-md border border-gray-200 p-8 animate-pulse">
    <div class="h-6 bg-gray-300 rounded w-48 mb-6"></div>
    
    <!-- Legend Skeleton -->
    <div class="flex justify-center gap-6 mb-4">
        <div class="flex items-center gap-2">
            <div class="w-4 h-4 bg-gray-300 rounded"></div>
            <div class="h-4 bg-gray-300 rounded w-16"></div>
        </div>
        <div class="flex items-center gap-2">
            <div class="w-4 h-4 bg-gray-300 rounded"></div>
            <div class="h-4 bg-gray-300 rounded w-16"></div>
        </div>
        <div class="flex items-center gap-2">
            <div class="w-4 h-4 bg-gray-300 rounded"></div>
            <div class="h-4 bg-gray-300 rounded w-16"></div>
        </div>
    </div>
    
    <!-- Chart Area Skeleton -->
    <div class="h-64 bg-gray-200 rounded-lg"></div>
</div>
@endif

{{-- Skeleton for News Card --}}
@if($type === 'news-card')
<div class="bg-white rounded-2xl border border-gray-300 p-3 animate-pulse" style="height: 120px;">
    <!-- Title Skeleton -->
    <div class="mb-2 h-12 space-y-2">
        <div class="h-4 bg-gray-300 rounded w-full"></div>
        <div class="h-4 bg-gray-300 rounded w-3/4"></div>
    </div>
    
    <!-- Bottom Section -->
    <div class="flex justify-between items-center gap-4 h-10">
        <!-- Source Skeleton -->
        <div class="flex-1">
            <div class="h-3 bg-gray-300 rounded w-24"></div>
        </div>
        
        <!-- Sentiment Badge Skeleton -->
        <div class="h-8 bg-gray-300 rounded w-20"></div>
    </div>
</div>
@endif

<style>
@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>