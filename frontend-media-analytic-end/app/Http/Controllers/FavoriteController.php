<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\BackendApiService;

class FavoriteController extends Controller
{
    protected BackendApiService $api;

    public function __construct(BackendApiService $api)
    {
        $this->api = $api;
    }

    /**
     * =========================
     * HALAMAN FAVORITE
     * =========================
     */
    public function index()
    {
        $response = $this->api->getFavorites(100);

        $favorites = ($response['success'] ?? false)
            ? $response['data']
            : [];

        return view('favorite', compact('favorites'));
    }

    /**
     * =========================
     * TOGGLE FAVORITE (AJAX)
     * POST /api/favorites/{id}/toggle
     * =========================
     */
    public function toggle($articleId)
    {
        // 1️⃣ cek status favorite
        $check = $this->api->checkFavorite($articleId);

        if (!($check['success'] ?? false)) {
            return response()->json([
                'success' => false,
                'message' => 'Gagal cek status favorit'
            ], 500);
        }

        $isFavorite = $check['data']['is_favorite'] ?? false;

        // 2️⃣ toggle ke backend
        $response = $isFavorite
            ? $this->api->removeFavorite($articleId)
            : $this->api->addFavorite($articleId);

        if (!($response['success'] ?? false)) {
            return response()->json([
                'success' => false,
                'message' => $response['message'] ?? 'Gagal toggle favorit'
            ], 400);
        }

        // 3️⃣ BALIKKAN STATUS BARU → UI SYNC
        return response()->json([
            'success'     => true,
            'is_favorite' => !$isFavorite
        ]);
    }
}
