<?php

use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Session;

use App\Http\Controllers\DashboardController;
use App\Http\Controllers\FavoriteController;
use App\Http\Controllers\HistoryController;
use App\Http\Controllers\MasterDataController;

/*
|--------------------------------------------------------------------------
| ROOT
|--------------------------------------------------------------------------
*/
Route::get('/', function () {

    // Kalau login → dashboard
    if (auth()->check()) {
        return redirect()->route('dashboard');
    }

    // Kalau guest → dashboard
    if (session('is_guest')) {
        return redirect()->route('dashboard');
    }

    // Default → login
    return redirect()->route('login');
});


/*
|--------------------------------------------------------------------------
| Guest Login
|--------------------------------------------------------------------------
*/
Route::get('/guest-login', function () {

    // Reset session lama
    auth()->logout();
    session()->invalidate();
    session()->regenerateToken();

    // Aktifkan guest
    session(['is_guest' => true]);

    return redirect()->route('dashboard');

})->name('guest.login');


/*
|--------------------------------------------------------------------------
| Logout (Auth + Guest)
|--------------------------------------------------------------------------
*/
Route::post('/logout', function () {

    auth()->logout();
    session()->forget('is_guest');

    request()->session()->invalidate();
    request()->session()->regenerateToken();

    return redirect()->route('login');

})->name('logout');


/*
|--------------------------------------------------------------------------
| Dashboard + Search (Auth & Guest)
|--------------------------------------------------------------------------
*/
Route::middleware(['auth.or.guest'])->group(function () {

    // Dashboard
    Route::get('/dashboard', [DashboardController::class, 'index'])
        ->name('dashboard');

    // Search
    Route::get('/search-results', [DashboardController::class, 'search'])
        ->name('search.results');


    // API Proxy
    Route::get('/api/v1/article/{id}', function ($id) {

        try {

            $backendUrl = env('BACKEND_API_URL', 'http://localhost:5000');

            $response = Http::timeout(10)
                ->get("{$backendUrl}/v1/article/{$id}");

            if ($response->successful()) {
                return response()->json($response->json());
            }

            return response()->json([
                'error' => 'Failed to fetch article'
            ], $response->status());

        } catch (\Exception $e) {

            return response()->json([
                'error'   => 'Backend connection failed',
                'message' => $e->getMessage()
            ], 500);
        }

    })->name('api.article.show');

});


/*
|--------------------------------------------------------------------------
| AUTH ONLY (WAJIB LOGIN)
|--------------------------------------------------------------------------
*/
Route::middleware(['auth'])->group(function () {

    // Favorite
    Route::get('/favorite', [FavoriteController::class, 'index'])
        ->name('favorite');

    Route::post('/api/favorites/{articleId}/toggle', [FavoriteController::class, 'toggle'])
        ->name('favorites.toggle');


    // ================= HISTORY =================

    Route::get('/history', [HistoryController::class, 'index'])
        ->name('history');

    Route::get('/history/detail', [HistoryController::class, 'detail'])
        ->name('history.detail');

    // Hapus satu
    Route::delete('/api/history/{historyId}', [HistoryController::class, 'delete'])
        ->name('history.delete');

    // Hapus semua  ✅ INI YANG HILANG
    Route::delete('/api/history', [HistoryController::class, 'clearAll'])
        ->name('history.clearAll');


    /*
    | Master Data
    */
    Route::get('/master-data', [MasterDataController::class, 'index'])
        ->name('master-data');

    Route::get('/api/sources',
        [MasterDataController::class, 'getSources'])
        ->name('sources.index');

    Route::post('/api/sources',
        [MasterDataController::class, 'store'])
        ->name('sources.store');

    Route::put('/api/sources/{id}',
        [MasterDataController::class, 'update'])
        ->name('sources.update');

    Route::delete('/api/sources/{id}',
        [MasterDataController::class, 'destroy'])
        ->name('sources.destroy');

});


/*
|--------------------------------------------------------------------------
| AUTH ROUTES (Breeze)
|--------------------------------------------------------------------------
*/
require __DIR__ . '/auth.php';
